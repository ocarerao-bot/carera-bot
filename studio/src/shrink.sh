#!/bin/bash
n=$1
ffmpeg -y -loglevel error -i /home/claude/vid/scenes/$n.mp4 -c:v libx264 -preset medium -crf 27 -pix_fmt yuv420p -r 30 -an -movflags +faststart /home/claude/vid/small/$n.tmp.mp4 && mv /home/claude/vid/small/$n.tmp.mp4 /home/claude/vid/small/$n.mp4 && echo shrunk $n
