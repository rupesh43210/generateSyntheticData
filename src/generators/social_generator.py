import random
from datetime import date, timedelta, datetime
from typing import List, Dict, Optional, Tuple
import string

from src.core.variability import VariabilityEngine
from pydantic import BaseModel, Field


class SocialMediaAccount(BaseModel):
    platform: str
    username: str
    display_name: str
    bio: Optional[str] = None
    follower_count: int
    following_count: int
    post_count: int
    account_created_date: date
    is_verified: bool = False
    is_private: bool = False
    profile_picture_url: str
    last_activity_date: date
    engagement_rate: float  # Percentage
    primary_content_type: str  # Photos, Videos, Text, Mixed


class OnlineAccount(BaseModel):
    platform: str
    username: str
    email_used: str
    account_type: str  # Free, Premium, Business
    account_created_date: date
    last_login_date: date
    subscription_status: str  # Active, Expired, Free
    privacy_settings: Dict[str, bool]
    two_factor_enabled: bool


class DigitalFootprint(BaseModel):
    primary_email_domains: List[str]
    backup_emails: List[str]
    phone_numbers_linked: List[str]
    recovery_questions: List[str]
    common_passwords_patterns: List[str]  # Obfuscated patterns, not actual passwords
    security_question_themes: List[str]


class OnlinePresence(BaseModel):
    social_media_accounts: List[SocialMediaAccount] = Field(default_factory=list)
    online_accounts: List[OnlineAccount] = Field(default_factory=list)
    digital_footprint: DigitalFootprint
    preferred_communication: List[str]  # Email, Text, Social Media, Phone
    online_activity_level: str  # Low, Moderate, High, Very High
    digital_privacy_awareness: str  # Low, Moderate, High
    tech_savviness: str  # Beginner, Intermediate, Advanced, Expert


class SocialMediaGenerator:
    """Generator for comprehensive social media and online presence data"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Social media platforms with popularity by age group
        self.platforms_by_age = {
            "18-24": {
                "TikTok": 0.65,
                "Instagram": 0.75,
                "Snapchat": 0.70,
                "Twitter": 0.40,
                "Facebook": 0.45,
                "LinkedIn": 0.25,
                "YouTube": 0.85,
                "Discord": 0.55,
                "Reddit": 0.50,
                "Twitch": 0.35
            },
            "25-34": {
                "Instagram": 0.70,
                "Facebook": 0.65,
                "Twitter": 0.45,
                "LinkedIn": 0.55,
                "TikTok": 0.45,
                "YouTube": 0.80,
                "Snapchat": 0.40,
                "Discord": 0.30,
                "Reddit": 0.45,
                "Pinterest": 0.35
            },
            "35-44": {
                "Facebook": 0.75,
                "Instagram": 0.55,
                "LinkedIn": 0.65,
                "Twitter": 0.40,
                "YouTube": 0.75,
                "Pinterest": 0.45,
                "TikTok": 0.25,
                "Snapchat": 0.20,
                "Reddit": 0.30,
                "WhatsApp": 0.60
            },
            "45-54": {
                "Facebook": 0.80,
                "LinkedIn": 0.60,
                "YouTube": 0.70,
                "Instagram": 0.40,
                "Twitter": 0.35,
                "Pinterest": 0.40,
                "WhatsApp": 0.55,
                "TikTok": 0.15,
                "Reddit": 0.20,
                "Nextdoor": 0.25
            },
            "55+": {
                "Facebook": 0.75,
                "YouTube": 0.65,
                "LinkedIn": 0.45,
                "Pinterest": 0.35,
                "Instagram": 0.25,
                "Twitter": 0.25,
                "WhatsApp": 0.45,
                "TikTok": 0.08,
                "Nextdoor": 0.30,
                "Skype": 0.40
            }
        }
        
        # Username patterns and generators
        self.username_patterns = [
            "{first_name}{last_name}",
            "{first_name}.{last_name}",
            "{first_name}_{last_name}",
            "{first_name}{last_initial}",
            "{first_initial}{last_name}",
            "{first_name}{birth_year}",
            "{first_name}{random_number}",
            "{nickname}{random_number}",
            "{hobby}{first_name}",
            "{adjective}{noun}"
        ]
        
        # Common username components
        self.adjectives = [
            "cool", "awesome", "super", "mega", "ultra", "happy", "sunny", "bright",
            "smart", "clever", "swift", "bold", "brave", "quiet", "calm", "wild",
            "free", "true", "real", "blue", "red", "green", "golden", "silver"
        ]
        
        self.nouns = [
            "tiger", "eagle", "wolf", "lion", "bear", "hawk", "shark", "dragon",
            "star", "moon", "sun", "fire", "thunder", "lightning", "storm", "ocean",
            "mountain", "river", "forest", "sky", "dream", "warrior", "hunter", "rider"
        ]
        
        self.hobbies = [
            "gamer", "reader", "writer", "artist", "musician", "dancer", "runner",
            "hiker", "swimmer", "cyclist", "photographer", "traveler", "chef", "baker"
        ]
        
        # Bio templates by platform
        self.bio_templates = {
            "Instagram": [
                "✨ Living my best life | 📍 {location} | 💕 {hobby}",
                "🌟 {profession} | 📚 {interest} enthusiast | 🎵 Music lover",
                "Adventure seeker 🗻 | Dog mom 🐕 | Coffee addict ☕",
                "Creating memories one photo at a time 📸",
                "Just a {adjective} soul living in a {adjective} world 🌍",
                "{hobby} | {hobby} | {location} native",
                "Blessed 🙏 | {profession} | Family first 👨‍👩‍👧‍👦"
            ],
            "Twitter": [
                "{profession} | Opinions are my own | {location}",
                "Passionate about {interest} and {interest} | RT ≠ endorsement",
                "Making the world a better place, one tweet at a time",
                "{hobby} enthusiast | {location} based | DMs open",
                "Thoughts on {interest}, {interest}, and life",
                "Professional {profession} | Amateur {hobby}",
                "Living in {location} | Dreaming of {interest}"
            ],
            "LinkedIn": [
                "{profession} at {company} | Passionate about {interest}",
                "Experienced {profession} | {skill} specialist | {location}",
                "Helping organizations with {skill} | {education} graduate",
                "{profession} | {years}+ years experience | Always learning",
                "Connecting {interest} with {interest} | Open to opportunities"
            ],
            "TikTok": [
                "Just here for the vibes ✨",
                "{hobby} content | {age} | {location}",
                "Making people smile one video at a time 😊",
                "Chaotic {adjective} energy | {hobby} enthusiast",
                "Your daily dose of {interest} content"
            ]
        }
        
        # Online platforms and services
        self.online_platforms = {
            "Shopping": ["Amazon", "eBay", "Etsy", "Target", "Walmart", "Best Buy", "Costco"],
            "Streaming": ["Netflix", "Hulu", "Disney+", "Amazon Prime", "Apple TV+", "HBO Max", "Spotify", "Apple Music"],
            "Productivity": ["Google Workspace", "Microsoft 365", "Dropbox", "OneDrive", "iCloud", "Notion", "Trello"],
            "Gaming": ["Steam", "PlayStation Network", "Xbox Live", "Nintendo Switch Online", "Epic Games", "Twitch"],
            "Financial": ["PayPal", "Venmo", "Cash App", "Zelle", "Mint", "Credit Karma", "Robinhood"],
            "Travel": ["Airbnb", "Booking.com", "Expedia", "Uber", "Lyft", "DoorDash", "Grubhub"],
            "News": ["Apple News", "Google News", "Reddit", "Medium", "Substack", "The New York Times"],
            "Health": ["MyFitnessPal", "Fitbit", "Apple Health", "Strava", "Headspace", "Calm"],
            "Dating": ["Tinder", "Bumble", "Hinge", "Match.com", "eHarmony", "OkCupid"],
            "Professional": ["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "Monster", "CareerBuilder"]
        }
        
        # Email domain preferences by age and type
        self.email_domains = {
            "mainstream": ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"],
            "professional": ["gmail.com", "outlook.com", "company.com"],
            "older": ["aol.com", "yahoo.com", "hotmail.com", "comcast.net", "verizon.net"],
            "privacy": ["protonmail.com", "tutanota.com", "startmail.com"],
            "custom": ["fastmail.com", "hey.com", "me.com"]
        }
        
        # Content types and themes
        self.content_types = {
            "Instagram": ["Photos", "Stories", "Reels", "IGTV"],
            "TikTok": ["Short Videos", "Challenges", "Trends"],
            "Twitter": ["Text", "Threads", "Retweets"],
            "YouTube": ["Long Videos", "Shorts", "Live Streams"],
            "LinkedIn": ["Professional Posts", "Articles", "Industry News"],
            "Facebook": ["Mixed", "Photos", "Life Updates", "Shared Content"]
        }
    
    def get_age_group(self, age: int) -> str:
        """Determine age group for platform preferences"""
        if age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 45:
            return "35-44"
        elif age < 55:
            return "45-54"
        else:
            return "55+"
    
    def generate_username(self, first_name: str, last_name: str, birth_year: int, 
                         platform: str) -> str:
        """Generate realistic username for platform"""
        # Clean names for username
        first_clean = ''.join(c for c in first_name.lower() if c.isalnum())
        last_clean = ''.join(c for c in last_name.lower() if c.isalnum())
        
        # Platform-specific preferences
        if platform in ["LinkedIn"]:
            # Professional platforms prefer real names
            patterns = [
                "{first_name}.{last_name}",
                "{first_name}{last_name}",
                "{first_name}{last_initial}"
            ]
        elif platform in ["TikTok", "Instagram", "Snapchat"]:
            # Creative platforms allow more variety
            patterns = [
                "{first_name}{random_number}",
                "{nickname}{random_number}",
                "{adjective}{noun}",
                "{hobby}{first_name}",
                "{first_name}_{adjective}"
            ]
        else:
            # General platforms
            patterns = self.username_patterns
        
        pattern = random.choice(patterns)
        
        # Generate components
        components = {
            "first_name": first_clean,
            "last_name": last_clean,
            "first_initial": first_clean[0] if first_clean else "x",
            "last_initial": last_clean[0] if last_clean else "x",
            "birth_year": str(birth_year),
            "random_number": str(random.randint(1, 9999)),
            "nickname": random.choice([first_clean[:4], first_clean]),
            "adjective": random.choice(self.adjectives),
            "noun": random.choice(self.nouns),
            "hobby": random.choice(self.hobbies)
        }
        
        # Apply pattern
        username = pattern.format(**components)
        
        # Add numbers if username might be taken (longer platforms)
        if len(username) < 6 or platform in ["Instagram", "Twitter", "TikTok"]:
            if random.random() < 0.6:
                username += str(random.randint(1, 999))
        
        # Platform-specific modifications
        if platform == "Twitter" and not username.startswith("@"):
            username = username[:15]  # Twitter username limit
        elif platform == "Instagram":
            username = username[:30]  # Instagram limit
        
        # Apply variability (typos, etc.)
        if self.variability and self.variability.should_apply(0.05):
            username = self.variability.introduce_typo(username)
        
        return username
    
    def generate_bio(self, platform: str, age: int, profession: str, 
                    location: str, interests: List[str]) -> Optional[str]:
        """Generate platform-appropriate bio/description"""
        if platform not in self.bio_templates:
            return None
        
        templates = self.bio_templates[platform]
        template = random.choice(templates)
        
        # Fill in template variables
        replacements = {
            "location": location,
            "profession": profession,
            "hobby": random.choice(self.hobbies),
            "interest": random.choice(interests) if interests else "technology",
            "adjective": random.choice(self.adjectives),
            "age": str(age),
            "company": "TechCorp",  # Could be made more dynamic
            "skill": random.choice(["innovation", "leadership", "strategy", "development"]),
            "education": random.choice(["University", "College", "Institute"]),
            "years": str(random.randint(1, 20))
        }
        
        bio = template
        for key, value in replacements.items():
            bio = bio.replace(f"{{{key}}}", value)
        
        # Platform-specific length limits
        if platform == "Twitter":
            bio = bio[:160]  # Twitter bio limit
        elif platform == "Instagram":
            bio = bio[:150]  # Instagram bio limit
        
        return bio
    
    def generate_follower_counts(self, platform: str, age: int, activity_level: str) -> Tuple[int, int, int]:
        """Generate realistic follower, following, and post counts"""
        # Base ranges by platform and activity level
        base_ranges = {
            "Instagram": {
                "Low": (50, 300, 20, 150, 10, 100),
                "Moderate": (200, 800, 100, 600, 50, 500),
                "High": (500, 2000, 300, 1200, 200, 1500),
                "Very High": (1000, 10000, 500, 2000, 500, 5000)
            },
            "Facebook": {
                "Low": (100, 400, 50, 200, 20, 200),
                "Moderate": (300, 800, 100, 400, 100, 800),
                "High": (500, 1500, 200, 800, 300, 2000),
                "Very High": (800, 3000, 400, 1500, 500, 5000)
            },
            "Twitter": {
                "Low": (20, 200, 50, 500, 10, 500),
                "Moderate": (100, 500, 200, 1000, 100, 2000),
                "High": (300, 1500, 500, 2000, 500, 8000),
                "Very High": (1000, 5000, 1000, 5000, 2000, 20000)
            },
            "TikTok": {
                "Low": (50, 500, 20, 200, 5, 50),
                "Moderate": (200, 2000, 100, 500, 20, 200),
                "High": (1000, 10000, 300, 1000, 100, 1000),
                "Very High": (5000, 100000, 500, 2000, 500, 5000)
            },
            "LinkedIn": {
                "Low": (50, 300, 50, 300, 5, 50),
                "Moderate": (200, 800, 100, 500, 20, 200),
                "High": (500, 2000, 300, 1000, 50, 500),
                "Very High": (1000, 5000, 500, 2000, 100, 1000)
            }
        }
        
        # Default ranges if platform not specified
        default_range = (50, 500, 50, 300, 10, 100)
        ranges = base_ranges.get(platform, {}).get(activity_level, default_range)
        
        followers = random.randint(ranges[0], ranges[1])
        following = random.randint(ranges[2], ranges[3])
        posts = random.randint(ranges[4], ranges[5])
        
        # Age adjustments (younger users tend to have more activity)
        if age < 25:
            followers = int(followers * random.uniform(1.2, 2.0))
            following = int(following * random.uniform(1.1, 1.5))
            posts = int(posts * random.uniform(1.3, 2.0))
        elif age > 50:
            followers = int(followers * random.uniform(0.5, 0.8))
            following = int(following * random.uniform(0.6, 0.9))
            posts = int(posts * random.uniform(0.4, 0.7))
        
        return followers, following, posts
    
    def generate_engagement_rate(self, platform: str, follower_count: int) -> float:
        """Generate realistic engagement rate based on platform and follower count"""
        # Base engagement rates by platform (industry averages)
        base_rates = {
            "Instagram": 1.22,
            "TikTok": 5.96,
            "Facebook": 0.25,
            "Twitter": 0.05,
            "LinkedIn": 0.54,
            "YouTube": 1.63
        }
        
        base_rate = base_rates.get(platform, 1.0)
        
        # Engagement typically decreases with follower count
        if follower_count < 1000:
            multiplier = random.uniform(1.5, 3.0)
        elif follower_count < 10000:
            multiplier = random.uniform(1.0, 2.0)
        elif follower_count < 100000:
            multiplier = random.uniform(0.5, 1.5)
        else:
            multiplier = random.uniform(0.1, 0.8)
        
        engagement_rate = base_rate * multiplier
        
        # Add some randomness
        engagement_rate *= random.uniform(0.7, 1.5)
        
        return round(min(engagement_rate, 20.0), 2)  # Cap at 20%
    
    def generate_social_media_account(self, platform: str, first_name: str, last_name: str,
                                    birth_year: int, age: int, profession: str,
                                    location: str, activity_level: str, 
                                    interests: List[str]) -> SocialMediaAccount:
        """Generate a complete social media account"""
        username = self.generate_username(first_name, last_name, birth_year, platform)
        display_name = f"{first_name} {last_name}"
        
        # Sometimes use nicknames or creative display names
        if platform in ["TikTok", "Instagram", "Snapchat"] and random.random() < 0.3:
            display_name = random.choice([
                first_name,
                f"{first_name} {last_name[0]}.",
                f"{random.choice(self.adjectives).title()} {first_name}",
                f"{first_name} {random.choice(['✨', '🌟', '💫', '🦋', '🌙'])}"
            ])
        
        bio = self.generate_bio(platform, age, profession, location, interests)
        
        followers, following, posts = self.generate_follower_counts(platform, age, activity_level)
        engagement_rate = self.generate_engagement_rate(platform, followers)
        
        # Account creation date (random time in the past)
        platform_ages = {
            "Facebook": 20,  # Facebook is older
            "LinkedIn": 22,
            "Twitter": 18,
            "Instagram": 14,
            "TikTok": 8,
            "Snapchat": 13,
            "YouTube": 19
        }
        
        max_account_age = min(platform_ages.get(platform, 10), age - 13)  # Can't have account before 13
        account_age = random.randint(1, max(1, max_account_age))
        created_date = date.today() - timedelta(days=account_age * 365 + random.randint(0, 364))
        
        # Last activity (recent for active users)
        if activity_level in ["High", "Very High"]:
            last_activity = date.today() - timedelta(days=random.randint(0, 7))
        elif activity_level == "Moderate":
            last_activity = date.today() - timedelta(days=random.randint(1, 30))
        else:
            last_activity = date.today() - timedelta(days=random.randint(7, 90))
        
        # Privacy settings (younger users more likely to be private)
        is_private = False
        if platform in ["Instagram", "TikTok"] and age < 25:
            is_private = random.random() < 0.4
        elif platform in ["Facebook"]:
            is_private = random.random() < 0.6  # Many Facebook profiles are private
        
        # Verification (very rare for regular users)
        is_verified = random.random() < 0.001  # 0.1% chance
        
        # Profile picture URL (placeholder)
        profile_pic = f"https://placeholder.pics/svg/400x400/DEDEDE/555555/{first_name[0]}{last_name[0]}"
        
        # Content type
        content_types = self.content_types.get(platform, ["Mixed"])
        primary_content = random.choice(content_types)
        
        return SocialMediaAccount(
            platform=platform,
            username=username,
            display_name=display_name,
            bio=bio,
            follower_count=followers,
            following_count=following,
            post_count=posts,
            account_created_date=created_date,
            is_verified=is_verified,
            is_private=is_private,
            profile_picture_url=profile_pic,
            last_activity_date=last_activity,
            engagement_rate=engagement_rate,
            primary_content_type=primary_content
        )
    
    def generate_online_account(self, platform: str, category: str, first_name: str,
                              last_name: str, primary_email: str, age: int) -> OnlineAccount:
        """Generate online account for various platforms"""
        username = self.generate_username(first_name, last_name, 2024 - age, platform)
        
        # Account types
        account_types = {
            "Shopping": ["Free", "Prime", "Premium"],
            "Streaming": ["Free", "Basic", "Premium", "Family"],
            "Productivity": ["Free", "Personal", "Business"],
            "Gaming": ["Free", "Plus", "Premium"],
            "Financial": ["Free", "Premium"],
            "Professional": ["Free", "Premium", "Business"]
        }
        
        account_type = random.choice(account_types.get(category, ["Free", "Premium"]))
        
        # Subscription status
        if account_type == "Free":
            subscription_status = "Free"
        else:
            subscription_status = random.choices(
                ["Active", "Expired", "Cancelled"],
                weights=[0.7, 0.2, 0.1]
            )[0]
        
        # Account creation date
        years_ago = random.randint(1, min(10, age - 13))
        created_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 364))
        
        # Last login
        if subscription_status == "Active":
            last_login = date.today() - timedelta(days=random.randint(0, 30))
        elif subscription_status == "Expired":
            last_login = date.today() - timedelta(days=random.randint(30, 365))
        else:
            last_login = date.today() - timedelta(days=random.randint(90, 730))
        
        # Privacy settings
        privacy_settings = {
            "public_profile": random.random() < 0.3,
            "show_activity": random.random() < 0.4,
            "allow_messages": random.random() < 0.6,
            "share_data": random.random() < 0.2,
            "targeted_ads": random.random() < 0.5
        }
        
        # Two-factor authentication (more likely for younger, tech-savvy users)
        two_factor_enabled = False
        if age < 40 and platform in ["Banking", "PayPal", "Google", "Apple"]:
            two_factor_enabled = random.random() < 0.6
        elif category in ["Financial", "Professional"]:
            two_factor_enabled = random.random() < 0.4
        else:
            two_factor_enabled = random.random() < 0.2
        
        return OnlineAccount(
            platform=platform,
            username=username,
            email_used=primary_email,
            account_type=account_type,
            account_created_date=created_date,
            last_login_date=last_login,
            subscription_status=subscription_status,
            privacy_settings=privacy_settings,
            two_factor_enabled=two_factor_enabled
        )
    
    def determine_activity_level(self, age: int, tech_savviness: str) -> str:
        """Determine online activity level based on age and tech skills"""
        base_weights = {
            "Low": 0.25,
            "Moderate": 0.40,
            "High": 0.25,
            "Very High": 0.10
        }
        
        # Age adjustments
        if age < 25:
            base_weights["High"] *= 2
            base_weights["Very High"] *= 3
        elif age < 35:
            base_weights["Moderate"] *= 1.5
            base_weights["High"] *= 1.5
        elif age > 55:
            base_weights["Low"] *= 2
            base_weights["Moderate"] *= 1.2
            base_weights["High"] *= 0.5
            base_weights["Very High"] *= 0.2
        
        # Tech savviness adjustments
        if tech_savviness == "Expert":
            base_weights["High"] *= 2
            base_weights["Very High"] *= 3
        elif tech_savviness == "Advanced":
            base_weights["Moderate"] *= 1.5
            base_weights["High"] *= 2
        elif tech_savviness == "Beginner":
            base_weights["Low"] *= 2
            base_weights["Moderate"] *= 1.2
            base_weights["High"] *= 0.5
        
        # Normalize weights
        total = sum(base_weights.values())
        normalized_weights = {k: v/total for k, v in base_weights.items()}
        
        levels = list(normalized_weights.keys())
        weights = list(normalized_weights.values())
        return random.choices(levels, weights=weights)[0]
    
    def generate_digital_footprint(self, first_name: str, last_name: str,
                                 age: int, birth_year: int) -> DigitalFootprint:
        """Generate digital footprint and online security information"""
        # Primary email domains (prefer by age)
        if age < 30:
            primary_domains = ["gmail.com", "icloud.com", "outlook.com"]
        elif age < 50:
            primary_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
        else:
            primary_domains = ["gmail.com", "yahoo.com", "aol.com", "hotmail.com", "comcast.net"]
        
        # Backup emails
        backup_emails = []
        num_backups = random.randint(1, 3)
        for _ in range(num_backups):
            domain = random.choice(self.email_domains["mainstream"])
            if domain not in primary_domains:
                backup_format = random.choice([
                    f"{first_name.lower()}.{last_name.lower()}",
                    f"{first_name.lower()}{last_name.lower()}",
                    f"{first_name.lower()}{birth_year}",
                    f"{first_name.lower()}_{last_name.lower()}"
                ])
                backup_emails.append(f"{backup_format}@{domain}")
        
        # Phone numbers linked (simulated)
        phone_numbers = [
            "***-***-" + str(random.randint(1000, 9999)) for _ in range(random.randint(1, 3))
        ]
        
        # Recovery questions themes
        recovery_themes = random.sample([
            "Pet names", "Mother's maiden name", "First school", "Childhood friend",
            "First car", "Favorite teacher", "Birth city", "Favorite food",
            "First job", "Childhood street"
        ], random.randint(2, 5))
        
        # Password patterns (obfuscated for privacy)
        password_patterns = random.sample([
            "Name + Year pattern", "Dictionary word + numbers", "Phrase-based",
            "Mixed case with symbols", "Sequential numbers", "Family names",
            "Sports teams + numbers", "Simple substitutions"
        ], random.randint(2, 4))
        
        # Security question themes
        security_themes = random.sample([
            "Personal history", "Family information", "Pets and animals",
            "Places lived", "School memories", "Entertainment preferences",
            "Food and restaurants", "Travel destinations"
        ], random.randint(3, 6))
        
        return DigitalFootprint(
            primary_email_domains=primary_domains,
            backup_emails=backup_emails,
            phone_numbers_linked=phone_numbers,
            recovery_questions=recovery_themes,
            common_passwords_patterns=password_patterns,
            security_question_themes=security_themes
        )
    
    def generate_online_presence(self, first_name: str, last_name: str, age: int,
                               birth_year: int, profession: str, location: str,
                               income: float, interests: List[str] = None) -> OnlinePresence:
        """Generate comprehensive online presence profile"""
        if interests is None:
            interests = ["technology", "travel", "food", "music"]
        
        # Determine tech savviness based on age and profession
        if "engineer" in profession.lower() or "developer" in profession.lower():
            tech_savviness = random.choice(["Advanced", "Expert"])
        elif age < 30:
            tech_savviness = random.choice(["Intermediate", "Advanced"])
        elif age < 50:
            tech_savviness = random.choice(["Beginner", "Intermediate", "Advanced"])
        else:
            tech_savviness = random.choice(["Beginner", "Intermediate"])
        
        # Determine activity level
        activity_level = self.determine_activity_level(age, tech_savviness)
        
        # Generate social media accounts based on age group
        age_group = self.get_age_group(age)
        platforms = self.platforms_by_age[age_group]
        
        social_accounts = []
        for platform, probability in platforms.items():
            if random.random() < probability:
                account = self.generate_social_media_account(
                    platform, first_name, last_name, birth_year, age,
                    profession, location, activity_level, interests
                )
                social_accounts.append(account)
        
        # Generate online accounts
        online_accounts = []
        primary_email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
        
        # Determine number of online accounts based on activity level
        account_counts = {
            "Low": random.randint(3, 8),
            "Moderate": random.randint(8, 15),
            "High": random.randint(15, 25),
            "Very High": random.randint(25, 40)
        }
        
        num_accounts = account_counts[activity_level]
        
        # Select platforms across categories
        all_platforms = []
        for category, platforms_list in self.online_platforms.items():
            num_from_category = random.randint(0, min(3, len(platforms_list)))
            selected = random.sample(platforms_list, num_from_category)
            for platform in selected:
                all_platforms.append((platform, category))
        
        # Generate accounts for selected platforms
        for platform, category in random.sample(all_platforms, min(num_accounts, len(all_platforms))):
            account = self.generate_online_account(
                platform, category, first_name, last_name, primary_email, age
            )
            online_accounts.append(account)
        
        # Generate digital footprint
        digital_footprint = self.generate_digital_footprint(first_name, last_name, age, birth_year)
        
        # Preferred communication methods
        comm_preferences = []
        if age < 30:
            comm_preferences = random.sample(
                ["Text", "Social Media", "Email", "Video Call"], 
                random.randint(2, 3)
            )
        elif age < 50:
            comm_preferences = random.sample(
                ["Email", "Text", "Phone", "Social Media"],
                random.randint(2, 3)
            )
        else:
            comm_preferences = random.sample(
                ["Phone", "Email", "Text"],
                random.randint(1, 2)
            )
        
        # Privacy awareness based on age and tech savviness
        if tech_savviness in ["Advanced", "Expert"]:
            privacy_awareness = random.choice(["Moderate", "High"])
        elif age > 50:
            privacy_awareness = random.choice(["Low", "Moderate"])
        else:
            privacy_awareness = random.choice(["Low", "Moderate", "High"])
        
        return OnlinePresence(
            social_media_accounts=social_accounts,
            online_accounts=online_accounts,
            digital_footprint=digital_footprint,
            preferred_communication=comm_preferences,
            online_activity_level=activity_level,
            digital_privacy_awareness=privacy_awareness,
            tech_savviness=tech_savviness
        )