#!/bin/sh

uvicorn app:app --host "0.0.0.0" --port 3000 --workers 1 --reload
