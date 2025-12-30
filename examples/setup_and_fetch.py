"""
Interactive setup and data fetcher for twscrape.
This script helps you add your Twitter account and fetch data from @dagsen.

Usage:
    python examples/setup_and_fetch.py
"""

import asyncio
import getpass
import os
import sys

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twscrape import API, gather


async def setup_account(api: API):
    """Interactive account setup."""
    print("\n" + "=" * 60)
    print("TWITTER ACCOUNT SETUP")
    print("=" * 60)
    print("\nTo fetch Twitter data, you need to add your Twitter account.")
    print("Your credentials will be stored locally in accounts.db")
    print("\nNote: If you have 2FA enabled, you'll need your email to receive")
    print("      the verification code during login.\n")

    username = input("Twitter username: ").strip()
    password = getpass.getpass("Twitter password: ")
    email = input("Email address (for verification): ").strip()
    email_password = getpass.getpass("Email password (for IMAP access): ")

    # Optional: cookies for direct login without password flow
    print("\nOptional: If you have cookies from your browser session,")
    print("you can paste them here (or press Enter to skip):")
    print("Format: 'auth_token=xxx; ct0=xxx; ...'")
    cookies = input("Cookies (optional): ").strip()

    # Optional: proxy
    print("\nOptional: Proxy for this account (e.g., http://user:pass@host:port)")
    proxy = input("Proxy (optional): ").strip()

    try:
        await api.pool.add_account(
            username=username,
            password=password,
            email=email,
            email_password=email_password,
            cookies=cookies if cookies else None,
            proxy=proxy if proxy else None
        )
        print(f"\nAccount @{username} added successfully!")

        if not cookies:
            print("\nAttempting to login...")
            print("(This may take a moment. If 2FA is enabled, check your email.)")
            await api.pool.login_all()
            print("Login attempt completed.")

        # Check account status
        stats = await api.pool.stats()
        print(f"\nAccount pool status: {stats}")

        return True
    except Exception as e:
        print(f"\nError adding account: {e}")
        return False


async def fetch_dagsen_data(api: API, target_username: str = "dagsen"):
    """Fetch data for the target user."""
    print("\n" + "=" * 60)
    print(f"FETCHING DATA FOR @{target_username}")
    print("=" * 60)

    try:
        # Get user profile
        print(f"\nFetching profile for @{target_username}...")
        user = await api.user_by_login(target_username)

        if not user:
            print(f"User @{target_username} not found.")
            return

        print("\n--- PROFILE ---")
        print(f"ID: {user.id}")
        print(f"Username: @{user.username}")
        print(f"Display Name: {user.displayname}")
        print(f"Bio: {user.rawDescription}")
        print(f"Location: {user.location}")
        print(f"Created: {user.created}")
        print(f"Followers: {user.followersCount:,}")
        print(f"Following: {user.friendsCount:,}")
        print(f"Tweets: {user.statusesCount:,}")
        print(f"Likes: {user.favouritesCount:,}")
        print(f"Verified: {user.verified} | Blue: {user.blue}")
        print(f"Profile URL: {user.url}")
        print(f"Profile Image: {user.profileImageUrl}")

        # Fetch recent tweets
        print("\n--- RECENT TWEETS (last 10) ---")
        tweet_count = 0
        async for tweet in api.user_tweets(user.id, limit=10):
            tweet_count += 1
            print(f"\n[{tweet_count}] {tweet.date}")
            content = tweet.rawContent
            if len(content) > 280:
                content = content[:277] + "..."
            print(f"    {content}")
            print(f"    Likes: {tweet.likeCount:,} | RTs: {tweet.retweetCount:,} | Replies: {tweet.replyCount:,}")

        if tweet_count == 0:
            print("  No tweets found or account may be protected.")

        # Fetch some followers
        print("\n--- SAMPLE FOLLOWERS (first 5) ---")
        follower_count = 0
        async for follower in api.followers(user.id, limit=5):
            follower_count += 1
            print(f"  @{follower.username} - {follower.displayname}")

        if follower_count == 0:
            print("  No followers data retrieved.")

        # Fetch who they follow
        print("\n--- SAMPLE FOLLOWING (first 5) ---")
        following_count = 0
        async for following in api.following(user.id, limit=5):
            following_count += 1
            print(f"  @{following.username} - {following.displayname}")

        if following_count == 0:
            print("  No following data retrieved.")

        print("\n" + "=" * 60)
        print("DATA FETCH COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nError fetching data: {e}")
        import traceback
        traceback.print_exc()


async def main():
    print("=" * 60)
    print("TWSCRAPE - Twitter Data Fetcher")
    print("=" * 60)

    api = API()

    # Check existing accounts
    stats = await api.pool.stats()
    print(f"\nCurrent account pool: {stats}")

    if stats.get("total", 0) == 0:
        print("\nNo accounts configured.")
        response = input("\nWould you like to add your Twitter account now? (y/n): ").strip().lower()

        if response == 'y':
            success = await setup_account(api)
            if not success:
                print("\nFailed to setup account. Exiting.")
                return
        else:
            print("\nYou need to add an account to fetch data.")
            print("\nAlternatively, you can add accounts via CLI:")
            print("  twscrape add_accounts accounts.txt username:password:email:email_password")
            print("  twscrape login_accounts")
            return
    elif stats.get("active", 0) == 0:
        print("\nNo active accounts. Attempting to login existing accounts...")
        await api.pool.login_all()
        stats = await api.pool.stats()
        print(f"Updated pool status: {stats}")

        if stats.get("active", 0) == 0:
            print("\nCould not login. Please check your credentials.")
            return

    # Fetch data for @dagsen
    await fetch_dagsen_data(api, "dagsen")


if __name__ == "__main__":
    asyncio.run(main())
