"""
Fetch comprehensive Twitter/X data for a specific user.
This script retrieves profile info, tweets, followers, and following.

Usage:
    python examples/fetch_user_data.py --username dagsen
    python examples/fetch_user_data.py --username dagsen --tweets-limit 50
"""

import argparse
import asyncio
import json
import os
from datetime import datetime

from twscrape import API, gather


async def fetch_user_profile(api: API, username: str):
    """Fetch user profile information."""
    print(f"\n{'='*60}")
    print(f"Fetching profile for @{username}...")
    print(f"{'='*60}")

    try:
        user = await api.user_by_login(username)
        if user:
            print(f"\nProfile Information:")
            print(f"  ID: {user.id}")
            print(f"  Username: @{user.username}")
            print(f"  Display Name: {user.displayname}")
            print(f"  Description: {user.rawDescription}")
            print(f"  Location: {user.location}")
            print(f"  Created: {user.created}")
            print(f"  Followers: {user.followersCount:,}")
            print(f"  Following: {user.friendsCount:,}")
            print(f"  Tweets: {user.statusesCount:,}")
            print(f"  Likes: {user.favouritesCount:,}")
            print(f"  Media: {user.mediaCount:,}")
            print(f"  Listed: {user.listedCount:,}")
            print(f"  Verified: {user.verified}")
            print(f"  Blue: {user.blue}")
            print(f"  Blue Type: {user.blueType}")
            print(f"  Profile Image: {user.profileImageUrl}")
            print(f"  Banner: {user.profileBannerUrl}")
            print(f"  URL: {user.url}")
            if user.pinnedIds:
                print(f"  Pinned Tweet IDs: {user.pinnedIds}")
            return user
        else:
            print(f"User @{username} not found.")
            return None
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None


async def fetch_user_tweets(api: API, user_id: int, limit: int = 20):
    """Fetch user's recent tweets."""
    print(f"\n{'='*60}")
    print(f"Fetching tweets (limit: {limit})...")
    print(f"{'='*60}")

    tweets = []
    try:
        async for tweet in api.user_tweets(user_id, limit=limit):
            tweets.append(tweet)
            print(f"\n[{len(tweets)}] Tweet ID: {tweet.id}")
            print(f"    Date: {tweet.date}")
            print(f"    Content: {tweet.rawContent[:200]}{'...' if len(tweet.rawContent) > 200 else ''}")
            print(f"    Likes: {tweet.likeCount:,} | Retweets: {tweet.retweetCount:,} | Replies: {tweet.replyCount:,} | Quotes: {tweet.quoteCount:,}")
            if tweet.viewCount:
                print(f"    Views: {tweet.viewCount:,}")
            if tweet.hashtags:
                print(f"    Hashtags: {', '.join(tweet.hashtags)}")
            if tweet.media.photos:
                print(f"    Photos: {len(tweet.media.photos)}")
            if tweet.media.videos:
                print(f"    Videos: {len(tweet.media.videos)}")
            if tweet.quotedTweet:
                print(f"    Quotes Tweet ID: {tweet.quotedTweet.id}")
            if tweet.retweetedTweet:
                print(f"    Retweet of: {tweet.retweetedTweet.id}")
    except Exception as e:
        print(f"Error fetching tweets: {e}")

    print(f"\nTotal tweets fetched: {len(tweets)}")
    return tweets


async def fetch_user_media(api: API, user_id: int, limit: int = 20):
    """Fetch user's media tweets."""
    print(f"\n{'='*60}")
    print(f"Fetching media tweets (limit: {limit})...")
    print(f"{'='*60}")

    media_tweets = []
    try:
        async for tweet in api.user_media(user_id, limit=limit):
            media_tweets.append(tweet)
            print(f"\n[{len(media_tweets)}] Media Tweet ID: {tweet.id}")
            print(f"    Date: {tweet.date}")
            print(f"    Photos: {len(tweet.media.photos)}")
            print(f"    Videos: {len(tweet.media.videos)}")
            for i, photo in enumerate(tweet.media.photos):
                print(f"      Photo {i+1}: {photo.url}")
            for i, video in enumerate(tweet.media.videos):
                best = sorted(video.variants, key=lambda x: x.bitrate)[-1] if video.variants else None
                if best:
                    print(f"      Video {i+1}: {best.url}")
    except Exception as e:
        print(f"Error fetching media: {e}")

    print(f"\nTotal media tweets fetched: {len(media_tweets)}")
    return media_tweets


async def fetch_followers(api: API, user_id: int, limit: int = 50):
    """Fetch user's followers."""
    print(f"\n{'='*60}")
    print(f"Fetching followers (limit: {limit})...")
    print(f"{'='*60}")

    followers = []
    try:
        async for user in api.followers(user_id, limit=limit):
            followers.append(user)
            print(f"  @{user.username} ({user.displayname}) - {user.followersCount:,} followers")
    except Exception as e:
        print(f"Error fetching followers: {e}")

    print(f"\nTotal followers fetched: {len(followers)}")
    return followers


async def fetch_following(api: API, user_id: int, limit: int = 50):
    """Fetch accounts the user follows."""
    print(f"\n{'='*60}")
    print(f"Fetching following (limit: {limit})...")
    print(f"{'='*60}")

    following = []
    try:
        async for user in api.following(user_id, limit=limit):
            following.append(user)
            print(f"  @{user.username} ({user.displayname}) - {user.followersCount:,} followers")
    except Exception as e:
        print(f"Error fetching following: {e}")

    print(f"\nTotal following fetched: {len(following)}")
    return following


async def fetch_tweets_and_replies(api: API, user_id: int, limit: int = 20):
    """Fetch user's tweets and replies."""
    print(f"\n{'='*60}")
    print(f"Fetching tweets and replies (limit: {limit})...")
    print(f"{'='*60}")

    tweets = []
    try:
        async for tweet in api.user_tweets_and_replies(user_id, limit=limit):
            tweets.append(tweet)
            reply_info = ""
            if tweet.inReplyToUser:
                reply_info = f" [Reply to @{tweet.inReplyToUser.username}]"
            print(f"  [{len(tweets)}]{reply_info} {tweet.rawContent[:100]}...")
    except Exception as e:
        print(f"Error fetching tweets and replies: {e}")

    print(f"\nTotal tweets and replies fetched: {len(tweets)}")
    return tweets


async def save_data_to_json(data: dict, username: str, output_dir: str = "data"):
    """Save all collected data to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"{username}_{timestamp}.json")

    # Convert data to serializable format
    output = {}

    if data.get("user"):
        output["user"] = data["user"].dict()

    if data.get("tweets"):
        output["tweets"] = [t.dict() for t in data["tweets"]]

    if data.get("media_tweets"):
        output["media_tweets"] = [t.dict() for t in data["media_tweets"]]

    if data.get("followers"):
        output["followers"] = [u.dict() for u in data["followers"]]

    if data.get("following"):
        output["following"] = [u.dict() for u in data["following"]]

    if data.get("tweets_and_replies"):
        output["tweets_and_replies"] = [t.dict() for t in data["tweets_and_replies"]]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nData saved to: {filename}")
    return filename


async def main():
    parser = argparse.ArgumentParser(description="Fetch Twitter/X user data")
    parser.add_argument("--username", "-u", default="dagsen", help="Twitter username to fetch (default: dagsen)")
    parser.add_argument("--tweets-limit", "-t", type=int, default=20, help="Number of tweets to fetch (default: 20)")
    parser.add_argument("--media-limit", "-m", type=int, default=10, help="Number of media tweets to fetch (default: 10)")
    parser.add_argument("--followers-limit", "-f", type=int, default=50, help="Number of followers to fetch (default: 50)")
    parser.add_argument("--following-limit", "-g", type=int, default=50, help="Number of following to fetch (default: 50)")
    parser.add_argument("--replies-limit", "-r", type=int, default=20, help="Number of tweets+replies to fetch (default: 20)")
    parser.add_argument("--save", "-s", action="store_true", help="Save data to JSON file")
    parser.add_argument("--output-dir", "-o", default="data", help="Output directory for JSON files (default: data)")
    parser.add_argument("--db", default="accounts.db", help="Path to accounts database (default: accounts.db)")
    parser.add_argument("--profile-only", "-p", action="store_true", help="Only fetch profile information")
    args = parser.parse_args()

    print(f"Twitter/X Data Fetcher for @{args.username}")
    print(f"Database: {args.db}")
    print(f"{'='*60}")

    api = API(args.db)

    # Check if we have accounts
    stats = await api.pool.stats()
    print(f"Account pool stats: {stats}")

    if stats.get("total", 0) == 0:
        print("\nWARNING: No accounts in the pool!")
        print("You need to add Twitter accounts to use this tool.")
        print("\nTo add accounts, run:")
        print("  twscrape add_accounts accounts.txt username:password:email:email_password")
        print("  twscrape login_accounts")
        print("\nOr add accounts programmatically:")
        print('  await api.pool.add_account("username", "password", "email", "email_password")')
        print('  await api.pool.login_all()')
        return

    collected_data = {}

    # Fetch user profile
    user = await fetch_user_profile(api, args.username)
    if not user:
        print("Could not fetch user profile. Exiting.")
        return

    collected_data["user"] = user

    if args.profile_only:
        if args.save:
            await save_data_to_json(collected_data, args.username, args.output_dir)
        return

    # Fetch tweets
    if args.tweets_limit > 0:
        collected_data["tweets"] = await fetch_user_tweets(api, user.id, args.tweets_limit)

    # Fetch media tweets
    if args.media_limit > 0:
        collected_data["media_tweets"] = await fetch_user_media(api, user.id, args.media_limit)

    # Fetch tweets and replies
    if args.replies_limit > 0:
        collected_data["tweets_and_replies"] = await fetch_tweets_and_replies(api, user.id, args.replies_limit)

    # Fetch followers
    if args.followers_limit > 0:
        collected_data["followers"] = await fetch_followers(api, user.id, args.followers_limit)

    # Fetch following
    if args.following_limit > 0:
        collected_data["following"] = await fetch_following(api, user.id, args.following_limit)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"User: @{user.username} ({user.displayname})")
    print(f"Tweets fetched: {len(collected_data.get('tweets', []))}")
    print(f"Media tweets fetched: {len(collected_data.get('media_tweets', []))}")
    print(f"Tweets+Replies fetched: {len(collected_data.get('tweets_and_replies', []))}")
    print(f"Followers fetched: {len(collected_data.get('followers', []))}")
    print(f"Following fetched: {len(collected_data.get('following', []))}")

    # Save to JSON if requested
    if args.save:
        await save_data_to_json(collected_data, args.username, args.output_dir)


if __name__ == "__main__":
    asyncio.run(main())
