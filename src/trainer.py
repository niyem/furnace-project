import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from src.model_nn import FurnaceNet

def train_model(data_path, output_model_path):
    # 1. Load Data
    df = pd.read_csv(data_path)
    X = df.drop(columns=['TARGET_Avg_Efficiency']).values
    y = df['TARGET_Avg_Efficiency'].values.reshape(-1, 1)

    # 2. Scale Data
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.FloatTensor(y_train)
    X_test_t = torch.FloatTensor(X_test)
    y_test_t = torch.FloatTensor(y_test)

    # 3. Initialize Model
    model = FurnaceNet(input_dim=X_train.shape[1])
    criterion = nn.MSELoss()
    
    # Lower initial LR slightly (0.001 -> 0.0005) for stability
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5) 
    
    # ADDED SCHEDULER: Reduce LR if validation loss stalls for 20 epochs
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=20)

    # 4. Training Loop
    epochs = 600  # Increased slightly
    train_losses = []
    val_losses = []

    print(f"      [Info] Starting training for {epochs} epochs with Scheduler...")
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train_t)
        loss = criterion(outputs, y_train_t)
        loss.backward()
        optimizer.step()
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_out = model(X_test_t)
            val_loss = criterion(val_out, y_test_t)
        
        # Step the scheduler
        scheduler.step(val_loss)
        
        train_losses.append(loss.item())
        val_losses.append(val_loss.item())
        
        if epoch % 50 == 0:
            print(f"      Epoch {epoch}/{epochs} | Train: {loss.item():.4f} | Val: {val_loss.item():.4f}")

    torch.save(model.state_dict(), output_model_path)
    
    history = {
        'train_loss': train_losses,
        'val_loss': val_losses,
        'y_pred': scaler_y.inverse_transform(val_out.numpy()),
        'y_actual': scaler_y.inverse_transform(y_test_t.numpy())
    }
    return history