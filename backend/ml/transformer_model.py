"""
Transformer Model for NQ Price Prediction
Phase 3: The Architect
"""

import torch
import torch.nn as nn
import math
import logging

logger = logging.getLogger(__name__)

class PositionalEncoding(nn.Module):
    """
    Injects some information about the relative or absolute position of the tokens 
    in the sequence. The positional encodings have the same dimension as 
    the embeddings, so that the two can be summed.
    """
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        # Create constant positional encoding matrix with values from sin and cos
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x shape: [seq_len, batch_size, embedding_dim]
        return x + self.pe[:x.size(0), :]

class NQTransformer(nn.Module):
    """
    Transformer-based Time Series Classifier
    Input: [batch_size, seq_len, features]
    Output: [batch_size, 3] (DOWN, SIDEWAYS, UP)
    """
    def __init__(
        self, 
        feature_dim, 
        num_classes=3, 
        d_model=64, 
        nhead=4, 
        num_layers=2, 
        dropout=0.1
    ):
        super(NQTransformer, self).__init__()
        
        self.model_type = 'Transformer'
        self.feature_dim = feature_dim
        
        # Input projection to d_model size
        self.encoder = nn.Linear(feature_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        # Transformer Encoder Layers
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=d_model*4, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
        # Final classification head
        self.decoder = nn.Linear(d_model, num_classes)
        
        self.d_model = d_model
        
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.encoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()

    def forward(self, src):
        """
        Args:
            src: [batch_size, seq_len, feature_dim]
        Returns:
            output: [batch_size, num_classes]
        """
        # Transformer expects [seq_len, batch_size, d_model]
        src = src.permute(1, 0, 2) 
        
        src = self.encoder(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src)
        
        # Take the output of the last time step for classification
        # output shape: [seq_len, batch_size, d_model]
        output = output[-1, :, :]
        
        output = self.decoder(output)
        return output

if __name__ == "__main__":
    # Test initialization
    logging.basicConfig(level=logging.INFO)
    
    batch_size = 32
    seq_len = 60
    feature_dim = 34 # From our Phase 2 results
    
    print(f"Testing Transformer with: Batch={batch_size}, Seq={seq_len}, Feat={feature_dim}")
    
    model = NQTransformer(feature_dim=feature_dim)
    
    # Create dummy input
    dummy_input = torch.randn(batch_size, seq_len, feature_dim)
    
    # Forward pass
    output = model(dummy_input)
    
    print(f"Output shape: {output.shape}") # Should be [32, 3]
    print("Transformer initialization successful!")
