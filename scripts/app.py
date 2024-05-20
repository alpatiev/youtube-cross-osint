import json
import re
import sys
import argparse
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Just flush the output.
def print_status(message):
    sys.stdout.write('\r' + message)
    sys.stdout.flush()

# Channel ID, will be used later
def get_channel_id(custom_url, youtube):
    print_status("> Extracting channel ID...")
    match = re.search(r'@([^\/\?&]+)', custom_url)
    if not match:
        raise ValueError("> Could not extract username from URL.")
    username = match.group(1)
    request = youtube.search().list(part="snippet", q=username, type="channel")
    response = request.execute()
    if 'items' not in response or not response['items']:
        raise ValueError("> No channel found for the given username.")
    return response['items'][0]['snippet']['channelId'], username

# Get video data with paging by 50 items, both for --short and --full
def get_videos(channel_id, youtube):
    print_status("> Fetching videos...")
    videos = []
    next_page_token = None
    while True:
        request = youtube.search().list(part="snippet", channelId=channel_id, maxResults=50, order="date", pageToken=next_page_token)
        response = request.execute()
        for item in response.get('items', []):
            video_id = item['id'].get('videoId')
            title = item['snippet']['title']
            published_at = item['snippet']['publishedAt']
            description = item['snippet'].get('description', '')
            if video_id:
                video_details = {
                    'id': video_id,
                    'title': title,
                    'description': description,
                    'date_uploaded': published_at,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'comments': []
                }
                videos.append(video_details)
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return videos

# Just for the views counter
def get_video_statistics(video_id, youtube):
    print_status(f"> Fetching statistics for video ID: {video_id}")
    request = youtube.videos().list(part="statistics,snippet", id=video_id)
    response = request.execute()
    if 'items' not in response or not response['items']:
        return {'views': 0, 'description': ''}
    item = response['items'][0]
    views_count = int(item['statistics'].get('viewCount', 0))
    full_description = item['snippet'].get('description', '')
    return {'views': views_count, 'description': full_description}

# Comments if available, empty array otherwise
def get_video_comments(video_id, youtube):
    print_status(f"> Fetching comments for video ID: {video_id}")
    comments = []
    next_page_token = None
    while True:
        try:
            request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100, pageToken=next_page_token)
            response = request.execute()
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'user_id': comment.get('authorChannelId', {}).get('value', ''),
                    'context': comment['textOriginal'],
                    'likes': comment['likeCount'],
                    'timestamp': comment['publishedAt']
                })
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except HttpError as e:
            print_status(f"> Comments are closed for video ID: {video_id}")
            break
    return comments

# Save to json to data folder, called data/channel_<name>.json
# To reuse it later I saved ID there
def generate_json(videos, channel_id, youtube, full, channel_name):
    print_status("> Generating JSON data...")
    total_size_kb = 0
    for video in videos:
        video_id = video['id']
        stats = get_video_statistics(video_id, youtube)
        video['views_count'] = stats['views']
        video['description'] = stats['description']
        if full:
            video['comments'] = get_video_comments(video_id, youtube)
        video_size = len(json.dumps(video).encode('utf-8'))
        total_size_kb += video_size / 1024
    result = {
        "target_channel_id": channel_id,
        "total_videos": len(videos),
        "videos_list": videos[::-1]
    }
    os.makedirs('data', exist_ok=True)
    with open(f'data/channel_{channel_name}.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)
    print_status(f"> Finished. Total videos: {len(videos)}, Batch size: {total_size_kb:.2f} KB\n")

# Just for updating settings.json
def set_api_key(key):
    config_path = os.path.join('settings', 'config.json')
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
    config['api_key'] = key
    os.makedirs('settings', exist_ok=True)
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, ensure_ascii=False, indent=4)
    print_status(f"> API key updated in {config_path}")

# Parse args, call methods
def main():
    parser = argparse.ArgumentParser(description="YouTube Channel Scraper")
    parser.add_argument('-s', '--short', action='store_true', help="Scrap videos without comments")
    parser.add_argument('-f', '--full', action='store_true', help="Scrap videos with comments")
    parser.add_argument('-u', '--url', type=str, required='--short' in sys.argv or '--full' in sys.argv, help="Channel URL")
    parser.add_argument('-k', '--api-key', type=str, help="Set API key")
    args = parser.parse_args()
    if args.api_key:
        set_api_key(args.api_key)
        sys.exit(0)
    api_key = ""
    config_path = os.path.join('settings', 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as config_file:
            config = json.load(config_file)
            api_key = config.get('api_key', '')
    if not api_key:
        print("> Set API key first in settings/config.json")
        sys.exit(0)
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        channel_id, channel_name = get_channel_id(args.url, youtube)
        videos = get_videos(channel_id, youtube)
        generate_json(videos, channel_id, youtube, args.full, channel_name)
    except Exception as e:
        print_status(f"> {e}")
    finally:
        if not args.short and not args.full:
            parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
