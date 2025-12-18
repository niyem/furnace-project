import torch
import torch.nn as nn

class FurnaceNet(nn.Module):
    def __init__(self, input_dim):
        super(FurnaceNet, self).__init__()
        
        # IMPROVED ARCHITECTURE
        # 1. Slightly smaller layers to prevent memorization (Overfitting)
        # 2. Batch Normalization to force convergence
        # 3. Higher Dropout (0.2) to improve generalization
        
        self.layer1 = nn.Linear(input_dim, 32)
        self.bn1 = nn.BatchNorm1d(32)
        
        self.layer2 = nn.Linear(32, 16)
        self.bn2 = nn.BatchNorm1d(16)
        
        self.layer3 = nn.Linear(16, 8)
        
        self.output = nn.Linear(8, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2) # increased from 0.1

    def forward(self, x):
        # Layer 1
        x = self.layer1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.dropout(x)
        
        # Layer 2
        x = self.layer2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.dropout(x)
        
        # Layer 3
        x = self.layer3(x)
        x = self.relu(x)
        
        # Output
        x = self.output(x)
        return x