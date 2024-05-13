#!/bin/bash

source requirements.sh

color
heading "Movie" "Encoder"
install "FFmpeg" "jq" "Python" "Python-pip" "yt-dlp" "ffmpeg" "jq" "python3" "python3-pip" "yt-dlp"

heading "Movie" "Encoder"

failed() {
    echo -e "${c[31]}$1 Failed!!!${c[0]}"
    exit 1
}

source="/sdcard/Movies/.source"
target="/sdcard/Movies/"

mkdir -p "$source"
cd "$source"
file=$(ls *.mp4)
title="${file%.*}"

if [ -f "${title}.webp" ]; then
    ffmpeg -y -i "${title}.webp" \
        -map_metadata -1 -map_metadata:s -1 -map_metadata:g -1 -map_chapters -1 -map_chapters:s -1 -map_chapters:g -1 \
        "${title}.jpg" >/dev/null 2>&1 ||
        failed Conversion
fi

language=$(ls "${title}"*".srt" 2>/dev/null)
language=${language%.*}
language=${language##*.}

ffmpeg -y -i "${title}.mp4" -i "${title}.srt" \
    -map 0:v -map 0:a -map 1:s \
    -map_metadata -1 -map_metadata:s -1 -map_metadata:g -1 -map_chapters -1 -map_chapters:s -1 -map_chapters:g -1 \
    -metadata title="${title}" -metadata:s:s:0 language="${language}" \
    -c copy \
    -attach "${title}.jpg" -metadata:s:t filename="$title" -metadata:s:t mimetype=image/jpeg \
    "${target}/${title}.mkv" ||
    failed Conversion
