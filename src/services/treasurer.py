import google.auth
import json
import re

import requests
from flask import Flask, request

import pandas as pd
import numpy as np 
from pydantic import BaseModel


dues=pd.read_csv('G:\My Drive\TauBot\src\services\dues.csv')

