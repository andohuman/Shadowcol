import librosa
import numpy as np
import torch
from time import time
import os
import argparse
from utils import SiameseNet

parser = argparse.ArgumentParser(description='Live test SiameseNet')
parser.add_argument('--model_location', '-l', type=str, default='model/{}-epoch-{}.pth')
parser.add_argument('--epoch', '-e', type=int, default=None)
parser.add_argument('--device', '-d', type=str, default=None)
parser.add_argument('--ref', '-r', type=str, default='references/')
parser.add_argument('-t', '--target', type=str, default='data/test.wav')
args = parser.parse_args()

if not args.device:
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'

print('Loading model')
model = SiameseNet().to(device=args.device)
model.load_state_dict(torch.load(args.model_location.format('model',args.epoch), map_location=args.device))
model.train()

RATE = 16000

def preprocess(audio=None):
    audio_trimmed = librosa.effects.trim(audio, top_db=7)[0]
    audio_center = librosa.util.pad_center(audio_trimmed[:4000], 4000)
    audio_mfcc = librosa.feature.mfcc(y=audio_center, sr=RATE)
    audio_tensor = torch.tensor(audio_mfcc[None,None])
    
    return audio_tensor.to(device=args.device)

refs = {
        'up':preprocess(librosa.load(os.path.join(args.ref,'up.wav'), sr=RATE)[0]),
        'down':preprocess(librosa.load(os.path.join(args.ref,'down.wav'), sr=RATE)[0]),
        'sil':preprocess(librosa.load(os.path.join(args.ref,'sil.wav'), sr=RATE)[0])
        }
target = preprocess(librosa.load(args.target, sr=RATE)[0])


scores = []
start = time()

scores.append(model([refs['up'], target]).cpu().detach().numpy()) 
scores.append(model([refs['down'], target]).cpu().detach().numpy()) 
scores.append(model([refs['sil'], target]).cpu().detach().numpy()) 

print('Up : ',scores[0],' Down : ', scores[1], ' Silence : ', scores[2], ' time : ', time()-start)

'''    if scores.index(max(scores)) == 0:
        print('Up')
    elif scores.index(max(scores)) == 1:
        print('Down')
    elif scores.index(max(scores)) == 2:
        print('Sil')
'''
