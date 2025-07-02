"""
Communication Patterns and Contact Networks Generator - Creates comprehensive communication data and social networks
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
import uuid

class CommunicationType(Enum):
    PHONE_CALL = "phone_call"
    TEXT_MESSAGE = "text_message"
    EMAIL = "email"
    VIDEO_CALL = "video_call"
    SOCIAL_MEDIA = "social_media"
    INSTANT_MESSAGE = "instant_message"
    VOICE_MESSAGE = "voice_message"

class ContactRelationship(Enum):
    FAMILY = "family"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    ACQUAINTANCE = "acquaintance"
    BUSINESS = "business"
    ROMANTIC_PARTNER = "romantic_partner"
    NEIGHBOR = "neighbor"
    CLASSMATE = "classmate"
    PROFESSIONAL = "professional"
    OTHER = "other"

class CommunicationDirection(Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    MISSED = "missed"

class Platform(Enum):
    PHONE = "phone"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    SLACK = "slack"
    ZOOM = "zoom"
    TEAMS = "teams"
    SKYPE = "skype"

class Contact(BaseModel):
    contact_id: str
    name: str
    phone_number: Optional[str]
    email: Optional[str]
    relationship: ContactRelationship
    closeness_score: int  # 1-10, 10 being closest
    frequency_score: int  # 1-10, 10 being most frequent
    platforms: List[Platform]
    first_contact_date: datetime
    last_contact_date: datetime
    notes: Optional[str]
    is_emergency_contact: bool
    location: Optional[str]

class CommunicationRecord(BaseModel):
    record_id: str
    contact_id: str
    timestamp: datetime
    communication_type: CommunicationType
    direction: CommunicationDirection
    platform: Platform
    duration_seconds: Optional[int]  # For calls
    message_length: Optional[int]  # For texts/emails
    was_successful: bool
    location: Optional[str]
    group_conversation: bool
    participant_count: Optional[int]

class SocialNetworkNode(BaseModel):
    node_id: str
    contact_id: str
    centrality_score: float  # How central this contact is in the network
    cluster_id: str  # Which social cluster they belong to
    mutual_connections: int
    introduction_source: Optional[str]

class CommunicationPattern(BaseModel):
    daily_call_volume: int
    daily_text_volume: int
    daily_email_volume: int
    preferred_communication_times: List[str]  # e.g., ["morning", "evening"]
    preferred_platforms: List[Platform]
    response_time_minutes: int
    communication_style: str  # formal, casual, mixed
    group_vs_individual_preference: float  # 0-1, 1 being prefer groups

class CommunicationProfile(BaseModel):
    contacts: List[Contact]
    communication_records: List[CommunicationRecord]
    social_network: List[SocialNetworkNode]
    communication_patterns: CommunicationPattern
    total_contacts: int
    active_contacts_30_days: int
    emergency_contacts: List[str]  # List of contact IDs
    blocked_contacts: List[str]
    communication_statistics: Dict[str, Any]

class CommunicationGenerator:
    def __init__(self):
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson"
        ]
        
        self.email_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
            "icloud.com", "protonmail.com", "company.com", "university.edu"
        ]
        
        self.area_codes = [
            "212", "310", "415", "713", "312", "602", "404", "617", "206", "305",
            "702", "214", "480", "303", "818", "646", "323", "718", "917", "347"
        ]
        
        self.communication_clusters = {
            "family": {"size": (3, 8), "frequency": "high", "platforms": ["phone", "sms", "whatsapp"]},
            "work": {"size": (5, 15), "frequency": "medium", "platforms": ["email", "slack", "teams"]},
            "friends": {"size": (8, 25), "frequency": "medium", "platforms": ["sms", "instagram", "discord"]},
            "social": {"size": (10, 50), "frequency": "low", "platforms": ["facebook", "instagram", "twitter"]},
            "professional": {"size": (5, 20), "frequency": "low", "platforms": ["linkedin", "email"]}
        }

    def generate_communication_profile(self, age: int, occupation: str, lifestyle: str, location: str) -> CommunicationProfile:
        """Generate comprehensive communication profile"""
        
        # Generate contacts based on age and lifestyle
        contacts = self._generate_contacts(age, occupation, lifestyle, location)
        
        # Generate communication records for last 3 months
        communication_records = self._generate_communication_records(contacts, age, lifestyle)
        
        # Generate social network structure
        social_network = self._generate_social_network(contacts)
        
        # Analyze communication patterns
        communication_patterns = self._analyze_communication_patterns(communication_records, age, lifestyle)
        
        # Calculate statistics
        statistics = self._calculate_communication_statistics(contacts, communication_records)
        
        # Emergency contacts
        emergency_contacts = self._select_emergency_contacts(contacts)
        
        # Blocked contacts (small percentage)
        blocked_contacts = self._generate_blocked_contacts()
        
        # Active contacts in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_contacts = len([c for c in contacts if c.last_contact_date >= thirty_days_ago])
        
        return CommunicationProfile(
            contacts=contacts,
            communication_records=communication_records,
            social_network=social_network,
            communication_patterns=communication_patterns,
            total_contacts=len(contacts),
            active_contacts_30_days=active_contacts,
            emergency_contacts=[c.contact_id for c in emergency_contacts],
            blocked_contacts=blocked_contacts,
            communication_statistics=statistics
        )

    def _generate_contacts(self, age: int, occupation: str, lifestyle: str, location: str) -> List[Contact]:
        """Generate realistic contact list"""
        contacts = []
        
        # Determine total number of contacts based on age and lifestyle
        base_contacts = {
            "minimalist": 50,
            "average": 120,
            "social": 200,
            "extroverted": 300
        }
        
        lifestyle_key = lifestyle if lifestyle in base_contacts else "average"
        total_contacts = base_contacts[lifestyle_key] + random.randint(-20, 40)
        
        # Age adjustments
        if age < 25:
            total_contacts = int(total_contacts * 0.7)  # Younger people have fewer contacts
        elif age > 60:
            total_contacts = int(total_contacts * 0.8)  # Older people may have fewer active contacts
        
        # Generate contacts by cluster
        for cluster_type, config in self.communication_clusters.items():
            cluster_size = random.randint(*config["size"])
            
            # Adjust cluster size based on age and occupation
            if cluster_type == "work" and age < 22:
                cluster_size = int(cluster_size * 0.3)  # Students have fewer work contacts
            elif cluster_type == "family":
                cluster_size = max(3, cluster_size)  # Everyone has some family
            
            for _ in range(min(cluster_size, total_contacts - len(contacts))):
                contact = self._create_contact(cluster_type, age, location)
                contacts.append(contact)
                
                if len(contacts) >= total_contacts:
                    break
        
        # Fill remaining with random relationships
        while len(contacts) < total_contacts:
            relationship = random.choice(list(ContactRelationship))
            contact = self._create_contact(relationship.value, age, location)
            contacts.append(contact)
        
        return contacts

    def _create_contact(self, relationship_type: str, age: int, location: str) -> Contact:
        """Create a single contact"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        
        # Generate phone number
        area_code = random.choice(self.area_codes)
        phone_number = f"({area_code}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        
        # Generate email
        email_name = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99) if random.random() < 0.3 else ''}"
        email = f"{email_name}@{random.choice(self.email_domains)}"
        
        # Determine relationship
        if relationship_type in [rel.value for rel in ContactRelationship]:
            relationship = ContactRelationship(relationship_type)
        else:
            relationship = random.choice(list(ContactRelationship))
        
        # Closeness and frequency scores based on relationship
        closeness_frequency_map = {
            ContactRelationship.FAMILY: (7, 8),
            ContactRelationship.ROMANTIC_PARTNER: (10, 9),
            ContactRelationship.FRIEND: (6, 6),
            ContactRelationship.COLLEAGUE: (4, 7),
            ContactRelationship.ACQUAINTANCE: (3, 2),
            ContactRelationship.BUSINESS: (2, 3),
            ContactRelationship.NEIGHBOR: (4, 3),
            ContactRelationship.CLASSMATE: (5, 4),
            ContactRelationship.PROFESSIONAL: (3, 2),
            ContactRelationship.OTHER: (3, 3)
        }
        
        base_closeness, base_frequency = closeness_frequency_map.get(relationship, (3, 3))
        closeness_score = max(1, min(10, base_closeness + random.randint(-2, 2)))
        frequency_score = max(1, min(10, base_frequency + random.randint(-2, 2)))
        
        # Platforms based on relationship and age
        platforms = self._select_platforms_for_contact(relationship, age)
        
        # Contact dates
        first_contact_date = datetime.now() - timedelta(days=random.randint(30, 3650))
        last_contact_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Emergency contact (higher chance for family and romantic partners)
        is_emergency = relationship in [ContactRelationship.FAMILY, ContactRelationship.ROMANTIC_PARTNER] and random.random() < 0.6
        
        return Contact(
            contact_id=str(uuid.uuid4()),
            name=name,
            phone_number=phone_number if random.random() < 0.9 else None,
            email=email if random.random() < 0.8 else None,
            relationship=relationship,
            closeness_score=closeness_score,
            frequency_score=frequency_score,
            platforms=platforms,
            first_contact_date=first_contact_date,
            last_contact_date=last_contact_date,
            notes=f"Met through {random.choice(['work', 'school', 'friends', 'family', 'online', 'neighborhood'])}" if random.random() < 0.3 else None,
            is_emergency_contact=is_emergency,
            location=location if random.random() < 0.6 else f"{random.choice(['Boston', 'Seattle', 'Denver', 'Austin'])}, {random.choice(['MA', 'WA', 'CO', 'TX'])}"
        )

    def _select_platforms_for_contact(self, relationship: ContactRelationship, age: int) -> List[Platform]:
        """Select communication platforms for contact based on relationship and age"""
        platform_preferences = {
            ContactRelationship.FAMILY: [Platform.PHONE, Platform.SMS, Platform.WHATSAPP, Platform.EMAIL],
            ContactRelationship.ROMANTIC_PARTNER: [Platform.PHONE, Platform.SMS, Platform.WHATSAPP, Platform.INSTAGRAM],
            ContactRelationship.FRIEND: [Platform.SMS, Platform.INSTAGRAM, Platform.DISCORD, Platform.WHATSAPP],
            ContactRelationship.COLLEAGUE: [Platform.EMAIL, Platform.SLACK, Platform.TEAMS, Platform.PHONE],
            ContactRelationship.BUSINESS: [Platform.EMAIL, Platform.PHONE, Platform.LINKEDIN],
            ContactRelationship.PROFESSIONAL: [Platform.LINKEDIN, Platform.EMAIL],
            ContactRelationship.ACQUAINTANCE: [Platform.SMS, Platform.FACEBOOK, Platform.INSTAGRAM],
            ContactRelationship.NEIGHBOR: [Platform.SMS, Platform.PHONE, Platform.EMAIL],
            ContactRelationship.CLASSMATE: [Platform.SMS, Platform.INSTAGRAM, Platform.DISCORD],
            ContactRelationship.OTHER: [Platform.SMS, Platform.EMAIL]
        }
        
        base_platforms = platform_preferences.get(relationship, [Platform.SMS, Platform.EMAIL])
        
        # Age-based platform adjustments
        if age < 25:
            # Younger people prefer social media and messaging apps
            if Platform.INSTAGRAM not in base_platforms and random.random() < 0.7:
                base_platforms.append(Platform.INSTAGRAM)
            if Platform.DISCORD not in base_platforms and random.random() < 0.4:
                base_platforms.append(Platform.DISCORD)
        elif age > 50:
            # Older people prefer traditional communication
            base_platforms = [p for p in base_platforms if p not in [Platform.DISCORD, Platform.INSTAGRAM]]
            if Platform.EMAIL not in base_platforms:
                base_platforms.append(Platform.EMAIL)
        
        # Select 1-4 platforms
        num_platforms = random.randint(1, min(4, len(base_platforms)))
        return random.sample(base_platforms, num_platforms)

    def _generate_communication_records(self, contacts: List[Contact], age: int, lifestyle: str) -> List[CommunicationRecord]:
        """Generate communication records for last 3 months"""
        records = []
        
        # Communication volume based on age and lifestyle
        base_daily_volume = {
            "minimalist": 15,
            "average": 35,
            "social": 60,
            "extroverted": 100
        }
        
        lifestyle_key = lifestyle if lifestyle in base_daily_volume else "average"
        daily_volume = base_daily_volume[lifestyle_key]
        
        # Age adjustments
        if age < 25:
            daily_volume = int(daily_volume * 1.3)  # Young people communicate more
        elif age > 60:
            daily_volume = int(daily_volume * 0.7)  # Older people communicate less
        
        # Generate records for last 90 days
        for day in range(90):
            date = datetime.now() - timedelta(days=day)
            
            # Weekend vs weekday patterns
            is_weekend = date.weekday() >= 5
            day_volume = int(daily_volume * (0.8 if is_weekend else 1.0))
            
            # Generate communications for this day
            for _ in range(random.randint(max(1, day_volume - 10), day_volume + 10)):
                contact = self._select_contact_for_communication(contacts)
                if contact:
                    record = self._create_communication_record(contact, date)
                    records.append(record)
        
        return sorted(records, key=lambda x: x.timestamp, reverse=True)

    def _select_contact_for_communication(self, contacts: List[Contact]) -> Optional[Contact]:
        """Select contact for communication based on frequency scores"""
        if not contacts:
            return None
        
        # Weight contacts by frequency score
        weights = [contact.frequency_score for contact in contacts]
        return random.choices(contacts, weights=weights)[0]

    def _create_communication_record(self, contact: Contact, date: datetime) -> CommunicationRecord:
        """Create a single communication record"""
        # Select communication type based on contact's platforms
        platform = random.choice(contact.platforms)
        
        # Map platform to communication type
        platform_to_type = {
            Platform.PHONE: CommunicationType.PHONE_CALL,
            Platform.SMS: CommunicationType.TEXT_MESSAGE,
            Platform.EMAIL: CommunicationType.EMAIL,
            Platform.WHATSAPP: CommunicationType.TEXT_MESSAGE,
            Platform.FACEBOOK: CommunicationType.SOCIAL_MEDIA,
            Platform.INSTAGRAM: CommunicationType.SOCIAL_MEDIA,
            Platform.TWITTER: CommunicationType.SOCIAL_MEDIA,
            Platform.LINKEDIN: CommunicationType.SOCIAL_MEDIA,
            Platform.DISCORD: CommunicationType.INSTANT_MESSAGE,
            Platform.SLACK: CommunicationType.INSTANT_MESSAGE,
            Platform.ZOOM: CommunicationType.VIDEO_CALL,
            Platform.TEAMS: CommunicationType.VIDEO_CALL,
            Platform.SKYPE: CommunicationType.VIDEO_CALL
        }
        
        comm_type = platform_to_type.get(platform, CommunicationType.TEXT_MESSAGE)
        
        # Direction (60% outgoing, 35% incoming, 5% missed)
        direction = random.choices(
            [CommunicationDirection.OUTGOING, CommunicationDirection.INCOMING, CommunicationDirection.MISSED],
            weights=[60, 35, 5]
        )[0]
        
        # Random time during the day (weighted toward active hours)
        hour_weights = [1, 1, 1, 1, 1, 1, 2, 4, 6, 8, 8, 8, 8, 8, 8, 8, 8, 6, 4, 3, 2, 2, 1, 1]
        hour = random.choices(range(24), weights=hour_weights)[0]
        timestamp = date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        
        # Duration for calls
        duration = None
        if comm_type in [CommunicationType.PHONE_CALL, CommunicationType.VIDEO_CALL]:
            if direction == CommunicationDirection.MISSED:
                duration = 0
            else:
                # Duration based on relationship closeness
                base_duration = contact.closeness_score * 60  # Base seconds
                duration = random.randint(30, base_duration * 3)
        
        # Message length for text-based communications
        message_length = None
        if comm_type in [CommunicationType.TEXT_MESSAGE, CommunicationType.EMAIL, CommunicationType.INSTANT_MESSAGE]:
            if comm_type == CommunicationType.EMAIL:
                message_length = random.randint(50, 500)
            else:
                message_length = random.randint(10, 200)
        
        # Success rate (higher for closer contacts)
        success_rate = 0.9 + (contact.closeness_score / 100)
        was_successful = direction != CommunicationDirection.MISSED and random.random() < success_rate
        
        # Group conversation (more likely for certain platforms)
        group_platforms = [Platform.DISCORD, Platform.SLACK, Platform.WHATSAPP]
        group_conversation = platform in group_platforms and random.random() < 0.3
        participant_count = random.randint(3, 8) if group_conversation else None
        
        return CommunicationRecord(
            record_id=str(uuid.uuid4()),
            contact_id=contact.contact_id,
            timestamp=timestamp,
            communication_type=comm_type,
            direction=direction,
            platform=platform,
            duration_seconds=duration,
            message_length=message_length,
            was_successful=was_successful,
            location=contact.location if random.random() < 0.1 else None,
            group_conversation=group_conversation,
            participant_count=participant_count
        )

    def _generate_social_network(self, contacts: List[Contact]) -> List[SocialNetworkNode]:
        """Generate social network analysis"""
        network = []
        
        # Create clusters
        clusters = {}
        for contact in contacts:
            cluster_key = contact.relationship.value
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(contact)
        
        for contact in contacts:
            # Calculate centrality (simplified)
            centrality = (contact.closeness_score + contact.frequency_score) / 20.0
            
            # Mutual connections (estimated based on relationship type)
            mutual_connections = {
                ContactRelationship.FAMILY: random.randint(5, 15),
                ContactRelationship.COLLEAGUE: random.randint(3, 20),
                ContactRelationship.FRIEND: random.randint(2, 12),
                ContactRelationship.ACQUAINTANCE: random.randint(0, 5),
                ContactRelationship.BUSINESS: random.randint(1, 8),
                ContactRelationship.PROFESSIONAL: random.randint(2, 15),
                ContactRelationship.NEIGHBOR: random.randint(1, 6),
                ContactRelationship.CLASSMATE: random.randint(5, 25),
                ContactRelationship.ROMANTIC_PARTNER: random.randint(3, 10),
                ContactRelationship.OTHER: random.randint(0, 5)
            }.get(contact.relationship, 2)
            
            network.append(SocialNetworkNode(
                node_id=str(uuid.uuid4()),
                contact_id=contact.contact_id,
                centrality_score=round(centrality, 3),
                cluster_id=contact.relationship.value,
                mutual_connections=mutual_connections,
                introduction_source=random.choice(["mutual_friend", "work", "school", "family", "online", "event"]) if random.random() < 0.7 else None
            ))
        
        return network

    def _analyze_communication_patterns(self, records: List[CommunicationRecord], age: int, lifestyle: str) -> CommunicationPattern:
        """Analyze communication patterns from records"""
        if not records:
            return CommunicationPattern(
                daily_call_volume=0,
                daily_text_volume=0,
                daily_email_volume=0,
                preferred_communication_times=["morning"],
                preferred_platforms=[Platform.PHONE],
                response_time_minutes=60,
                communication_style="casual",
                group_vs_individual_preference=0.2
            )
        
        # Calculate daily volumes
        call_records = [r for r in records if r.communication_type == CommunicationType.PHONE_CALL]
        text_records = [r for r in records if r.communication_type == CommunicationType.TEXT_MESSAGE]
        email_records = [r for r in records if r.communication_type == CommunicationType.EMAIL]
        
        daily_call_volume = len(call_records) // 90  # 90 days of data
        daily_text_volume = len(text_records) // 90
        daily_email_volume = len(email_records) // 90
        
        # Preferred communication times
        hours = [r.timestamp.hour for r in records]
        morning_count = len([h for h in hours if 6 <= h < 12])
        afternoon_count = len([h for h in hours if 12 <= h < 17])
        evening_count = len([h for h in hours if 17 <= h < 22])
        
        preferred_times = []
        if morning_count >= max(afternoon_count, evening_count):
            preferred_times.append("morning")
        if afternoon_count >= max(morning_count, evening_count):
            preferred_times.append("afternoon")
        if evening_count >= max(morning_count, afternoon_count):
            preferred_times.append("evening")
        
        if not preferred_times:
            preferred_times = ["morning"]
        
        # Preferred platforms
        platform_counts = {}
        for record in records:
            platform_counts[record.platform] = platform_counts.get(record.platform, 0) + 1
        
        preferred_platforms = sorted(platform_counts.keys(), key=lambda p: platform_counts[p], reverse=True)[:3]
        
        # Response time (simplified estimate)
        response_time = random.randint(5, 120)  # 5 minutes to 2 hours
        
        # Communication style based on age
        if age < 30:
            communication_style = random.choice(["casual", "casual", "mixed"])
        elif age > 50:
            communication_style = random.choice(["formal", "mixed", "mixed"])
        else:
            communication_style = "mixed"
        
        # Group vs individual preference
        group_records = [r for r in records if r.group_conversation]
        group_preference = len(group_records) / len(records) if records else 0.2
        
        return CommunicationPattern(
            daily_call_volume=daily_call_volume,
            daily_text_volume=daily_text_volume,
            daily_email_volume=daily_email_volume,
            preferred_communication_times=preferred_times,
            preferred_platforms=preferred_platforms,
            response_time_minutes=response_time,
            communication_style=communication_style,
            group_vs_individual_preference=round(group_preference, 2)
        )

    def _calculate_communication_statistics(self, contacts: List[Contact], records: List[CommunicationRecord]) -> Dict[str, Any]:
        """Calculate comprehensive communication statistics"""
        if not records:
            return {}
        
        # Basic stats
        total_communications = len(records)
        successful_communications = len([r for r in records if r.was_successful])
        
        # By type
        type_counts = {}
        for record in records:
            type_counts[record.communication_type.value] = type_counts.get(record.communication_type.value, 0) + 1
        
        # By direction
        direction_counts = {}
        for record in records:
            direction_counts[record.direction.value] = direction_counts.get(record.direction.value, 0) + 1
        
        # By relationship
        contact_relationship_map = {c.contact_id: c.relationship.value for c in contacts}
        relationship_counts = {}
        for record in records:
            rel = contact_relationship_map.get(record.contact_id, "unknown")
            relationship_counts[rel] = relationship_counts.get(rel, 0) + 1
        
        # Average call duration
        call_records = [r for r in records if r.duration_seconds is not None and r.duration_seconds > 0]
        avg_call_duration = sum(r.duration_seconds for r in call_records) / len(call_records) if call_records else 0
        
        return {
            "total_communications": total_communications,
            "successful_communications": successful_communications,
            "success_rate": round(successful_communications / total_communications, 3),
            "communications_by_type": type_counts,
            "communications_by_direction": direction_counts,
            "communications_by_relationship": relationship_counts,
            "average_call_duration_seconds": round(avg_call_duration, 1),
            "total_contacts_contacted": len(set(r.contact_id for r in records)),
            "most_contacted_relationship": max(relationship_counts.items(), key=lambda x: x[1])[0] if relationship_counts else None
        }

    def _select_emergency_contacts(self, contacts: List[Contact]) -> List[Contact]:
        """Select emergency contacts from contact list"""
        emergency_candidates = [c for c in contacts if c.is_emergency_contact]
        
        # If no emergency contacts marked, select closest family/partners
        if not emergency_candidates:
            family_contacts = [c for c in contacts if c.relationship in [ContactRelationship.FAMILY, ContactRelationship.ROMANTIC_PARTNER]]
            emergency_candidates = sorted(family_contacts, key=lambda c: c.closeness_score, reverse=True)[:3]
        
        return emergency_candidates[:3]  # Max 3 emergency contacts

    def _generate_blocked_contacts(self) -> List[str]:
        """Generate list of blocked contact IDs"""
        # Small percentage of people have blocked contacts
        if random.random() < 0.3:
            num_blocked = random.randint(1, 5)
            return [str(uuid.uuid4()) for _ in range(num_blocked)]
        return []