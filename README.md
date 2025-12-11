# bluerov2_thesis

## Install python
```bash 
sudo apt update sudo apt install -y git python3 python3-venv python3-pip 
```

## Clone this repo
```bash 
git clone git@github.com:rifqijuli/bluerov2_thesis.git
```

## install this for Gstreamer plugin
```bash 
sudo apt install python3-gi python3-gi-cairo gir1.2-gobject-2.0 gir1.2-gst-plugins-base-1.0 gir1.2-gstreamer-1.0 libgirepository1.0-dev
```

## Make virtual environment
```bash 
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install --upgrade pip
```

Now we are inside Virtual Environment.

## Check Gi for Gstreamer
```bash 
python3 -c "import gi; print('gi imported OK')"
```

## Install requirements on pip
```bash 
pip install -r requirements.txt
```

If numpy error, change the numpy version on the requirements.txt according to the error.

## Install Pytorch
Go to https://pytorch.org/get-started/locally/ and follow the guide. In my case, it shows as this:
```bash 
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

## Install Ultralytics
Go to https://docs.ultralytics.com/quickstart/ and follow the guide. In my case, it shows as this:
```bash 
pip3 install -U ultralytics
```


