import torch
import torch.nn.functional as F
from torch_geometric.nn import GraphConv, global_mean_pool, GATConv, SAGEConv, SAGEConv, BatchNorm
import HyperParameters

### HYPER PARAMETERS ###
CLASSES = HyperParameters.CLASSES
BATCH_SIZE = HyperParameters.BATCH_SIZE
HIDDEN_UNITS = HyperParameters.HIDDEN_UNITS
OUTPUT_SHAPE = len(CLASSES)
LEARNING_RATE = HyperParameters.LEARNING_RATE
EPOCHS = HyperParameters.LEARNING_RATE

class GNN(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim=HIDDEN_UNITS, output_dim=OUTPUT_SHAPE, dropout_rate=HyperParameters.DROPOUT_RATE, NUM_HEADS=HyperParameters.NUM_HEADS):
        super(GNN, self).__init__()
        self.gconv1 = GATConv(input_dim, hidden_dim, heads=NUM_HEADS)
        self.gconv2 = GATConv(hidden_dim*NUM_HEADS, hidden_dim, heads=NUM_HEADS)
        self.gconv3 = GraphConv(hidden_dim*NUM_HEADS, hidden_dim)
        self.gconv4 = SAGEConv(hidden_dim, hidden_dim)

        self.dropout = torch.nn.Dropout(p=dropout_rate)
        
        self.fc1 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, output_dim)

    def forward(self, x, edge_index, batch):
        #Pass the data through the Graph Conv Layers
        x = F.relu(self.gconv1(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.gconv2(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.gconv3(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.gconv4(x, edge_index))
        #Aggregate the output using global_mean_pool
        x = global_mean_pool(x, batch)
        x = self.dropout(x)
        #Apply Non-linearity with relu
        x = F.relu(self.fc1(x))
        #Pass to the output layer, grabbing the prediction logits.
        x = self.fc2(x)
        
        return x #return prediction logits