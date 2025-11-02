import torch
print ("torch version:", torch.__version__)
print ("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print ("cuda device count:", torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        print ("cuda device", i, "name:", torch.cuda.get_device_name(i))
        print ("cuda device", i, "capability:", torch.cuda.get_device_capability(i))
        print ("cuda device", i, "properties:", torch.cuda.get_device_properties(i))
else:
    print ("No cuda devices available")