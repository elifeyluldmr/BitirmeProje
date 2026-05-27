"""
English synthetic email data generator.
Run: python src/generate_english_data.py
"""

import random
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

random.seed(1111)

NAMES = [
    "James Wilson", "Sarah Johnson", "Michael Brown", "Emily Davis", "Robert Miller",
    "Jessica Taylor", "David Anderson", "Ashley Thomas", "Daniel Jackson", "Amanda White",
    "Christopher Harris", "Stephanie Martin", "Matthew Thompson", "Lauren Garcia", "Joshua Martinez",
    "Megan Robinson", "Andrew Clark", "Brittany Rodriguez", "Ryan Lewis", "Samantha Lee",
    "Kevin Walker", "Rachel Hall", "Brian Allen", "Nicole Young", "Justin Hernandez",
    "Amber King", "Brandon Wright", "Melissa Lopez", "Tyler Hill", "Christina Scott",
    "Jonathan Green", "Stephanie Adams", "Nathan Baker", "Kayla Gonzalez", "Eric Nelson",
    "Danielle Carter", "Patrick Mitchell", "Heather Perez", "Jason Roberts", "Tiffany Turner",
]

BANKS = [
    "Chase Bank", "Bank of America", "Wells Fargo", "Citibank", "US Bank",
    "Capital One", "TD Bank", "PNC Bank", "Truist Bank", "HSBC",
    "Barclays", "Lloyds Bank", "NatWest", "Santander UK", "Regions Bank",
]

COURIERS = [
    "FedEx", "UPS", "USPS", "DHL", "Amazon Logistics",
    "OnTrac", "LaserShip", "Royal Mail", "Evri", "Hermes",
]

ECOMMERCE = [
    "Amazon", "eBay", "Walmart", "Target", "Best Buy",
    "Etsy", "ASOS", "Zara", "Nike", "Apple Store",
    "Newegg", "Wayfair", "Overstock", "H&M", "Shopify Store",
]

TECH_COMPANIES = [
    "Google", "Apple", "Microsoft", "Meta", "Instagram",
    "Facebook", "Twitter/X", "LinkedIn", "Netflix", "Spotify",
    "Dropbox", "PayPal", "Zoom", "TikTok", "Amazon",
]

AMOUNTS = [
    "$9.99", "$19.99", "$24.99", "$49.99", "$74.99",
    "$99.00", "$149.00", "$199.99", "$249.00", "$299.00",
    "$499.00", "$999.00", "$1,200.00", "$1,500.00", "$2,000.00",
    "$3,000.00", "$5,000.00", "$7,500.00", "$10,000.00", "$350.00",
]

TRACKING_NO = lambda: f"1Z{random.randint(100000000,999999999)}WW"
ORDER_NO    = lambda: f"#{random.randint(10000000,99999999)}"

DATES = [
    "January 5, 2025", "February 3, 2025", "March 1, 2025", "April 7, 2025",
    "May 5, 2025", "June 2, 2025", "July 4, 2025", "August 1, 2025",
    "September 8, 2025", "October 3, 2025", "November 11, 2025", "December 1, 2025",
    "January 10, 2026", "February 5, 2026", "March 15, 2026", "April 20, 2026",
]

TIMES = [
    "8:15 AM", "9:02 AM", "10:30 AM", "11:15 AM", "12:00 PM",
    "1:05 PM", "2:20 PM", "3:45 PM", "4:10 PM", "6:30 PM",
]

IP_ADDRESSES = [
    "185.234.56.78", "91.107.34.21", "46.20.198.5", "178.62.55.33",
    "95.211.32.44", "212.58.197.11", "82.221.105.6", "109.74.193.98",
    "45.133.1.45", "198.41.128.0",
]

FAKE_LINKS = [
    "https://secure-verify-account.net/login",
    "https://bankverification-portal.com/confirm",
    "https://account-security-alert.org/verify",
    "https://payment-confirm-now.net/process",
    "https://parcel-update-tracking.com/package",
    "https://gov-benefits-claim.org/apply",
    "https://tax-refund-portal.net/claim",
    "https://security-center-verify.com/confirm",
    "https://reward-claim-center.com/redeem",
    "https://urgent-account-action.net/verify",
]

CRYPTO   = ["Bitcoin", "Ethereum", "USDT", "BNB", "Solana", "XRP", "Dogecoin"]
CITIES   = ["New York", "Los Angeles", "Chicago", "Houston", "London", "Manchester", "Dallas", "Phoenix"]
SPORTS   = ["football", "basketball", "tennis", "running", "cycling", "yoga", "CrossFit", "golf"]
FOODS    = ["pizza", "pasta", "sushi", "tacos", "burgers", "steak", "ramen", "curry"]
HOBBIES  = ["photography", "painting", "gardening", "reading", "gaming", "cooking", "hiking", "music"]
UNIS     = ["State University", "City College", "Technical Institute", "Community College", "Online Academy"]


# â”€â”€ PHISHING â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _ph_bank():
    n, b, a, l, ip, d, t = random.choice(NAMES), random.choice(BANKS), random.choice(AMOUNTS), random.choice(FAKE_LINKS), random.choice(IP_ADDRESSES), random.choice(DATES), random.choice(TIMES)
    return random.choice([
        f"URGENT: Your {b} account has been temporarily suspended. Unusual activity detected: a transfer of {a} was attempted from IP {ip} on {d} at {t}. Verify your identity immediately: {l}",
        f"Dear {n}, your {b} online banking access has been locked due to multiple failed login attempts. Unlock your account within 24 hours: {l}",
        f"Security Alert from {b}: We detected a login from an unrecognized device ({ip}). If this was not you, secure your account now: {l}",
        f"Your {b} account requires immediate verification. A transaction of {a} is pending approval. Confirm or deny: {l}",
        f"{b} NOTICE: Your debit card has been flagged for suspicious activity on {d}. Verify now to avoid suspension: {l}",
        f"Action Required: {b} detected unusual sign-in activity on {d}. Verify your identity to continue online banking: {l}",
        f"Dear valued {b} customer, your account will be closed in 48 hours unless you complete identity verification: {l}",
        f"ALERT: A wire transfer of {a} has been initiated from your {b} account. If unauthorized, click here immediately: {l}",
        f"{b} Security Team: Your password was changed from IP {ip}. If you did not do this, recover your account: {l}",
        f"FINAL WARNING from {b}: Failure to verify within 12 hours will result in permanent suspension: {l}",
        f"Transaction Alert â€” {b}: A purchase of {a} was declined. Update your payment information now: {l}",
        f"Fraud Alert from {b}: An unauthorized purchase of {a} was made. Dispute this charge immediately: {l}",
    ])

def _ph_delivery():
    c, tr, l, a = random.choice(COURIERS), TRACKING_NO(), random.choice(FAKE_LINKS), random.choice(["$2.99","$4.50","$3.75","$5.25"])
    return random.choice([
        f"{c}: Your package {tr} could not be delivered. A customs fee of {a} is required. Pay now: {l}",
        f"NOTICE from {c}: Your shipment {tr} is on hold. Action required within 24 hours to avoid return: {l}",
        f"Delivery Attempt Failed â€” {c}: No one was home. Reschedule your delivery here: {l}",
        f"{c} Alert: Your parcel {tr} requires address confirmation before final delivery: {l}",
        f"Your {c} package is waiting. A storage fee of {a}/day is accumulating. Claim now: {l}",
        f"URGENT: {c} shipment {tr} will be returned to sender in 48 hours. Update preferences: {l}",
        f"{c} Delivery: Your package has been flagged by customs. Pay clearance fee of {a}: {l}",
        f"Package held at {c} facility. Verify your delivery address to release your parcel: {l}",
        f"{c}: Unable to deliver due to incomplete address. Update your details: {l}",
        f"Final attempt â€” {c}: Package {tr} will be destroyed if not claimed within 3 days: {l}",
    ])

def _ph_account():
    p, n, ip, l, d, t = random.choice(TECH_COMPANIES), random.choice(NAMES), random.choice(IP_ADDRESSES), random.choice(FAKE_LINKS), random.choice(DATES), random.choice(TIMES)
    return random.choice([
        f"Security Alert from {p}: New sign-in detected from {ip} on {d} at {t}. If not you, secure your account: {l}",
        f"Your {p} account password was changed on {d}. If you did not do this, recover your account: {l}",
        f"{p} Notice: Unusual activity detected. Your account has been temporarily restricted. Verify identity: {l}",
        f"Dear {n}, your {p} account is at risk. Unauthorized access attempts detected. Protect now: {l}",
        f"URGENT: Your {p} account will be permanently deleted due to inactivity unless you log in within 24 hours: {l}",
        f"{p} Security: Someone is trying to access your account from {ip}. Block this access: {l}",
        f"Your {p} account has been compromised. Reset your password immediately: {l}",
        f"Notice: Multiple failed login attempts on your {p} account. Verify your identity: {l}",
        f"{p} Account Warning: Your two-factor authentication has been disabled. Re-enable it now: {l}",
        f"Action Required: Complete identity verification for your {p} account to avoid suspension: {l}",
    ])

def _ph_prize():
    a, n, l = random.choice(AMOUNTS), random.choice(NAMES), random.choice(FAKE_LINKS)
    return random.choice([
        f"Congratulations {n}! You have been selected as our weekly winner. Claim your prize of {a}: {l}",
        f"YOU WON! Our random draw selected your email. Your cash reward of {a} is waiting. Claim now: {l}",
        f"WINNER NOTIFICATION: You won a {a} gift card from our loyalty program. Redeem here: {l}",
        f"Exclusive offer for {n}: You earned {a} in cashback rewards. Transfer to your bank: {l}",
        f"Your survey reward of {a} is ready to claim. Complete your profile to receive payment: {l}",
        f"Lucky Draw Result: Your entry won {a}! This offer expires in 24 hours. Claim winnings: {l}",
        f"FREE {a} Amazon Gift Card! Selected from millions of users. Click to claim: {l}",
        f"SPECIAL REWARD: As a valued customer, you have been awarded {a}. Accept your reward: {l}",
        f"You are the 1,000,000th visitor! Claim your prize of {a}. Limited time: {l}",
        f"{n}: A mystery box worth {a} is reserved in your name. Claim before midnight: {l}",
    ])

def _ph_tax():
    a, l, d = random.choice(AMOUNTS), random.choice(FAKE_LINKS), random.choice(DATES)
    return random.choice([
        f"IRS Notice: A tax refund of {a} has been issued. Claim your refund before {d}: {l}",
        f"HMRC Tax Refund: You are eligible for a refund of {a}. Submit your claim by {d}: {l}",
        f"Tax Authority Notice: Our records show you are owed {a}. Verify your details: {l}",
        f"URGENT: Unclaimed tax refund of {a} expires on {d}. Claim your money now: {l}",
        f"Government Benefit Alert: You qualify for a payment of {a}. Verify identity to receive funds: {l}",
        f"IRS: Your tax return has been processed. Refund of {a} will be deposited once you confirm bank details: {l}",
        f"Tax Refund: Due to overpayment, you are owed {a}. Complete verification to receive refund: {l}",
        f"Federal Tax Credit: You are eligible to receive {a} in unclaimed benefits. Apply now: {l}",
        f"NOTICE: Your government stimulus check of {a} is ready. Confirm your bank account: {l}",
        f"Tax Authority: Your refund of {a} needs updated bank details to process: {l}",
    ])

def _ph_crypto():
    c, a, l = random.choice(CRYPTO), random.choice(AMOUNTS), random.choice(FAKE_LINKS)
    return random.choice([
        f"URGENT: Your {c} wallet has been compromised. Transfer funds to a secure wallet now: {l}",
        f"Investment Alert: {c} is predicted to surge 500% this week. Invest {a} now: {l}",
        f"Your {c} transaction requires confirmation. Wallet will be locked in 2 hours: {l}",
        f"Congratulations! You received {a} worth of {c} as a bonus. Claim now: {l}",
        f"BREAKING: Major {c} airdrop event! Claim your free tokens before they run out: {l}",
        f"Double your {c} investment in 24 hours with our guaranteed trading bot. Join: {l}",
        f"{c} Network Alert: Your wallet has been flagged for suspicious activity. Verify ownership: {l}",
        f"Your {c} staking rewards of {a} are ready. Connect your wallet to receive: {l}",
        f"Last chance: {c} presale ends tonight. Get in before prices skyrocket: {l}",
        f"ALERT: Unauthorized withdrawal of {a} from your {c} account. Secure wallet now: {l}",
    ])

def _ph_job():
    a, l, n = random.choice(["$500/day","$3,000/week","$8,000/month","$120,000/year"]), random.choice(FAKE_LINKS), random.choice(NAMES)
    return random.choice([
        f"Dear {n}, we found your profile and would like to offer a remote position paying {a}. Apply now: {l}",
        f"Work from home: Earn {a} processing simple online tasks. No experience required. Start immediately: {l}",
        f"Job Offer: Hiring remote data entry specialists. Earn {a}. Send details to apply: {l}",
        f"URGENT HIRING: Package reshipping coordinator. Earn {a} working from home. Reply with your address.",
        f"Congratulations! Your resume was shortlisted for a position earning {a}. Complete application: {l}",
        f"Part-time job: Earn {a} completing simple online surveys. Join our team: {l}",
        f"Hiring now: Mystery shoppers in your area. Earn {a} per assignment. Register: {l}",
        f"Special recruitment: Selected for a high-paying remote role at {a}. Interview scheduled: {l}",
        f"Hiring: Social media evaluator. Work from home, earn {a}. Limited spots: {l}",
        f"Brand ambassador from home. Earn {a} plus bonuses. Apply today: {l}",
    ])

def _ph_subscription():
    p, a, l = random.choice(["Netflix","Amazon Prime","Spotify","Apple TV+","Disney+","Hulu"]), random.choice(["$9.99","$14.99","$19.99","$12.99"]), random.choice(FAKE_LINKS)
    return random.choice([
        f"Your {p} subscription payment of {a}/month has failed. Update billing info to continue: {l}",
        f"{p} Notice: Your account will be cancelled in 24 hours unless you verify your payment method: {l}",
        f"Final Notice â€” {p}: We were unable to charge {a} to your card. Update payment info now: {l}",
        f"{p}: Your free trial ends today. Provide payment details to continue access: {l}",
        f"Billing Alert from {p}: An unusual charge of {a} was attempted on your account. Review: {l}",
        f"Your {p} subscription has been paused due to an expired card. Reactivate your account: {l}",
        f"{p} Security: Your account login credentials were changed. If not you, secure now: {l}",
        f"Action Required: Verify your {p} account to claim your exclusive {a} discount: {l}",
        f"IMPORTANT: {p} is upgrading systems. All users must re-verify their accounts: {l}",
        f"{p} Reward: You've been selected for a 6-month free subscription. Claim free access: {l}",
    ])

def _ph_inheritance():
    a, n, c = random.choice(["$5,000,000","$2,500,000","$8,000,000","$3,750,000"]), random.choice(NAMES), random.choice(CITIES)
    return random.choice([
        f"Dear {n}, I am a lawyer representing a deceased client who shares your surname. You are entitled to {a}. Contact me confidentially.",
        f"CONFIDENTIAL: An unclaimed account worth {a} in {c} matches your name. Reply to claim.",
        f"I have a business proposition involving {a} in unclaimed funds. Your assistance is needed. All expenses covered.",
        f"A wealthy family in {c} wishes to transfer {a} to a trusted foreign partner. You will receive 30% commission.",
        f"A client passed away without heirs. Estate of {a} must be claimed within 30 days. You share the surname.",
        f"LOTTERY NOTIFICATION: Your email was randomly selected. Your prize is {a}. Contact us to claim.",
        f"UN Compensation Fund: You are entitled to {a} in humanitarian aid. Complete the claim form.",
        f"COMPENSATION ALERT: As a fraud victim, you qualify for {a} from the International Fraud Recovery Unit.",
        f"I discovered your contact through a mutual associate. I have {a} needing transfer. You will be rewarded.",
        f"I am the attorney to a late oil magnate. Estate worth {a} has no named beneficiary. You qualify to inherit.",
    ])

def _ph_tech_support():
    c, l, ip = random.choice(["Microsoft","Apple","Google","Norton","McAfee","Windows Defender"]), random.choice(FAKE_LINKS), random.choice(IP_ADDRESSES)
    return random.choice([
        f"CRITICAL ALERT from {c}: Your computer has been infected with a virus. Get help now: {l}",
        f"{c} Security Alert: Malware detected from IP {ip}. Your personal data is at risk: {l}",
        f"WARNING: Your {c} license has expired. Your computer is now unprotected. Renew: {l}",
        f"URGENT: {c} detected unusual network activity. Remote access may have been enabled: {l}",
        f"Your {c} account has been compromised. Install the security patch immediately: {l}",
        f"{c} Notice: Your device is sending out spam. This may indicate infection. Scan now: {l}",
        f"SYSTEM ALERT from {c}: 5 threats detected on your computer. Remove immediately: {l}",
        f"Mandatory {c} Update: Failure to install this patch may result in data loss. Update: {l}",
        f"{c} detected your computer is part of a botnet. Immediate action required: {l}",
        f"{c} Support: Unauthorized subscription upgrade. Dispute the charge: {l}",
    ])

def _ph_short():
    l, a = random.choice(FAKE_LINKS), random.choice(AMOUNTS)
    return random.choice([
        f"Your parcel could not be delivered. Pay $1.99 to reschedule: {l}",
        f"BANK ALERT: Suspicious transaction detected. Verify immediately: {l}",
        f"You won {a}! Claim your prize: {l}",
        f"Package held at facility. Confirm address: {l}",
        f"Your account has been locked. Unlock now: {l}",
        f"TAX REFUND of {a} pending. Claim here: {l}",
        f"Urgent: Verify your identity to avoid account closure: {l}",
        f"Free gift for you! Tap to claim: {l}",
        f"Your card was charged {a}. Dispute this: {l}",
        f"Congratulations! You've been selected. Claim reward: {l}",
        f"Final warning: Your account expires in 24hrs: {l}",
        f"Delivery failed. Pay customs fee $4.99: {l}",
    ])


# â”€â”€ NORMAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _no_work():
    n, d = random.choice(NAMES), random.choice(DATES)
    return random.choice([
        f"Hi {n}, just following up on the report. Have you had a chance to review the figures before the meeting?",
        f"Good morning team, a reminder that the quarterly review is scheduled for this Friday at 10 AM.",
        f"Hi all, I wanted to share the updated project timeline. We pushed the delivery by one week.",
        f"Dear {n}, thank you for joining the call today. I'll send the proposal by Thursday.",
        f"Team update: The client approved the latest design mockups. Proceeding to development phase!",
        f"Hi {n}, could you send me the Q3 sales data? I need it for the board presentation on {d}.",
        f"Reminder: Performance reviews are due by end of next week. Complete your self-assessment form.",
        f"Hi team, the office will be closed on {d} for the public holiday. Enjoy the long weekend!",
        f"Hi {n}, I wanted to circle back on the budget proposal. Let's discuss a few adjustments.",
        f"Thanks for the presentation yesterday, {n}. Very insightful. Sharing with leadership team.",
        f"The weekly standup has been moved to 2 PM on Tuesdays. Please update your calendars.",
        f"Hi, updated the shared drive with the latest marketing plan. Add your comments by Wednesday.",
    ])

def _no_shopping():
    s, o, a, c, tr, d = random.choice(ECOMMERCE), ORDER_NO(), random.choice(AMOUNTS), random.choice(COURIERS), TRACKING_NO(), random.choice(DATES)
    return random.choice([
        f"Your {s} order {o} has been confirmed. Total: {a}. Estimated delivery: {d}.",
        f"Great news! Your {s} order has shipped via {c}. Tracking: {tr}. Expected: {d}.",
        f"Your {s} order {o} has been delivered. We hope you enjoy your purchase!",
        f"Thank you for your purchase from {s}. Order for {a} is being processed.",
        f"Your {s} return has been processed. Refund of {a} within 5-7 business days.",
        f"New arrivals at {s}! Check our latest collection â€” free shipping on orders over $50.",
        f"Your {s} wishlist item is back in stock! Items are selling fast.",
        f"Order Reminder: You left items in your {s} cart. Complete your purchase before they sell out!",
        f"Thank you for shopping with {s}. Your loyalty points balance is now 1,250.",
        f"{s}: Your package was delivered to your mailbox today.",
        f"Your {s} subscription box for {d} is on its way!",
        f"{s} Order Update: Your item is backordered. Expected availability: {d}.",
    ])

def _no_personal():
    n, c = random.choice(NAMES), random.choice(CITIES)
    return random.choice([
        f"Hey {n}! Hope you're doing well. It's been too long! Are you free this weekend?",
        f"Hi! Just wanted to check in. How's the new job? Would love to catch up over coffee.",
        f"Hey, visiting {c} next week! Would be great to meet up if you're around.",
        f"Happy birthday! Hope you have an amazing day with good food and great friends!",
        f"Hey {n}, did you see the game last night? What a match! We should watch the next one together.",
        f"Hi! Just checking if you got my message. Are you coming to the party on Saturday?",
        f"Hey, thanks so much for your help last week. Let me know how I can return the favour!",
        f"Hi {n}, found an old photo of us from that trip to {c}. Made me nostalgic!",
        f"Hey! My sister is getting married in {c} next spring. Saving the date for you!",
        f"Hi, just wanted to let you know I'll be in town for a conference. Would love to catch up.",
        f"Are you still doing morning runs? I've been trying to get back into it.",
        f"Hi! Just got back from {c} â€” it was amazing. You have to visit!",
    ])

def _no_family():
    n, c = random.choice(NAMES), random.choice(CITIES)
    return random.choice([
        f"Hi sweetheart, Dad and I were wondering if you're coming home for the holidays. Let us know!",
        f"Hey sis! How are the kids? We haven't video called in a while. Free this weekend?",
        f"Hi {n}, Mom asked me to remind you about Sunday dinner. Don't be late!",
        f"Hi honey, just wanted to let you know grandma is doing much better after the procedure.",
        f"Hey bro, the family reunion is confirmed for July in {c}. Book your flights early!",
        f"Hi love, your sister asked if you could help her move next weekend.",
        f"Reminder â€” Dad's birthday is next Thursday! We're organising a surprise dinner.",
        f"Hi {n}, found some of your old things while cleaning the attic. Want me to keep them?",
        f"The kids drew pictures for you today and wanted me to send them. They miss you!",
        f"Family update: Aunt Martha had the baby! A healthy boy, 7 lbs 4 oz.",
        f"Hi sweetheart, I saw this recipe and thought of you. Sending it over!",
        f"Hi {n}, did you get the birthday card I sent? The post has been slow lately.",
    ])

def _no_health():
    n, d, t = random.choice(NAMES), random.choice(DATES), random.choice(TIMES)
    return random.choice([
        f"Dear {n}, this is a reminder of your upcoming appointment on {d} at {t}. Arrive 10 min early.",
        f"Your prescription is ready for pickup at our pharmacy. Open Mondayâ€“Saturday, 9 AM to 6 PM.",
        f"Health Reminder: Your annual physical is due. Schedule online or call our office.",
        f"Dear patient, your recent lab results are now available in your patient portal.",
        f"Have you had your flu shot this season? Free vaccines available at our clinic.",
        f"Dear {n}, your dental cleaning is scheduled for {d}. Call us 24 hours in advance to reschedule.",
        f"Reminder: Your eye exam is coming up on {d}. Bring your current glasses.",
        f"Health Tip: Staying hydrated is key. Aim for 8 glasses of water per day.",
        f"Your physical therapy session is confirmed for {d} at {t}. Wear comfortable clothing.",
        f"Your insurance has approved the referral to the specialist. Office will contact you within 5 days.",
        f"Dear {n}, a follow-up appointment has been scheduled after your recent visit on {d}.",
        f"Monthly Newsletter: Tips for better sleep, managing stress, and staying active.",
    ])

def _no_travel():
    c, d, a = random.choice(CITIES), random.choice(DATES), random.choice(AMOUNTS)
    return random.choice([
        f"Your flight to {c} on {d} has been confirmed. Check-in opens 24 hours before departure.",
        f"Hotel Booking Confirmed: Your stay in {c} from {d}. Check-in at 3 PM. Enjoy your visit!",
        f"Travel Reminder: Your trip to {c} is coming up! Check the local weather and pack accordingly.",
        f"Your rental car is booked for pickup in {c} on {d}. Full details in your booking confirmation.",
        f"Travel tip: Best restaurants in {c} are fully booked on weekends. Reserve in advance.",
        f"Your train ticket to {c} on {d} is confirmed. Download your e-ticket before travel.",
        f"Good news! Your travel insurance for the {c} trip has been approved.",
        f"Visa Application Update: Your visa for the upcoming trip has been approved.",
        f"Travel Review Request: How was your recent stay in {c}? Share your experience!",
        f"Your {c} tour package is confirmed. Itinerary and guide details sent 48 hours before arrival.",
        f"Flight Change Notice: Your flight to {c} has been rescheduled to {d}. Booking updated.",
        f"Packing reminder for {c}: comfortable shoes, travel adapter, and travel insurance documents.",
    ])

def _no_sports():
    s, n, d = random.choice(SPORTS), random.choice(NAMES), random.choice(DATES)
    return random.choice([
        f"Hey {n}! Great session today at {s} practice. You're really improving. See you Thursday!",
        f"Team Update: {s.capitalize()} training is moved to {d}. Same time, different location.",
        f"Your {s} league registration is confirmed. Season starts on {d}.",
        f"The {s} tournament has been approved. Sign-ups are open â€” register before spots fill up.",
        f"Reminder about the {s} charity event on {d}. It's going to be a great day!",
        f"Your personal training session for {s} is scheduled for {d}. Bring water and a towel.",
        f"Weekly workout challenge: Can you beat last week's {s} personal record?",
        f"Team announcement: Friendly {s} match against City FC on {d}. All members must attend.",
        f"Gym membership renewal: Your membership expires on {d}. Renew to keep your sessions.",
        f"The {s} class on {d} is fully booked. You've been added to the waitlist.",
        f"Congratulations {n}! You completed the 30-day {s} challenge. Here's your badge!",
        f"Sports nutrition tip: Fuel your {s} training with the right pre-workout meal.",
    ])

def _no_food():
    f_, n, c = random.choice(FOODS), random.choice(NAMES), random.choice(CITIES)
    return random.choice([
        f"Hey {n}! I tried that new {f_} place in {c} last night â€” absolutely incredible. Try it!",
        f"Recipe of the week: Easy homemade {f_} in under 30 minutes. Perfect for a weeknight!",
        f"Your table reservation for tonight at 7:30 PM is confirmed. We look forward to seeing you.",
        f"Your {f_} order is on its way. Estimated arrival: 25-35 minutes.",
        f"Hi! Are you free for dinner on Saturday? There's a great new {f_} restaurant near {c}.",
        f"Meal kit delivery: Your weekly box with {f_} ingredients will arrive on {random.choice(DATES)}.",
        f"Restaurant Newsletter: This month's special is our signature {f_} dish, locally sourced.",
        f"Cooking class reminder: Your {f_} masterclass is this Sunday at 11 AM. Bring your apron!",
        f"Friend recommendation: {n} shared a restaurant review â€” highly rated {f_} spot in {c}.",
        f"Food blog update: 10 best {f_} recipes for summer. Check it out!",
        f"Your grocery order is packed. Don't forget the {f_} ingredients you ordered!",
        f"Happy hour: 2-for-1 {f_} specials every Thursday evening at our downtown {c} location.",
    ])

def _no_tech():
    p, d = random.choice(TECH_COMPANIES), random.choice(DATES)
    return random.choice([
        f"Your {p} backup completed successfully on {d}. All data is securely stored.",
        f"{p} Product Update: Version 5.2 is now available with new features. Update now.",
        f"Monthly storage summary: You've used 12.4 GB of your {p} storage. Manage your files.",
        f"New feature alert from {p}: We've launched a new dashboard. Check it out!",
        f"Your {p} subscription renews on {d}. No action required unless you wish to make changes.",
        f"Tech Tip: Did you know {p} supports two-factor authentication? Enable it in settings.",
        f"Your weekly {p} activity summary: 8 tasks completed, collaboration with 5 team members.",
        f"{p} Security Update: We patched a vulnerability. No user action required.",
        f"App Update: The {p} mobile app has a redesigned interface and offline mode support.",
        f"Your {p} export is ready for download. File available for 7 days.",
        f"Community Forum: Join the discussion on the latest {p} features.",
        f"{p} Developer Update: API v3.0 is now in beta. Sign up to test the latest features.",
    ])

def _no_daily():
    n, c = random.choice(NAMES), random.choice(CITIES)
    return random.choice([
        f"Good morning! Reminder to take your vitamins and drink a glass of water before starting the day.",
        f"Hey {n}, I saw your post about moving to {c}! So exciting. How's the new place?",
        f"Quick note: I won't be able to make it to the gym tomorrow. Can we reschedule to Thursday?",
        f"Just finished reading that book you recommended. Couldn't put it down â€” it was fantastic!",
        f"Reminder: Car insurance renewal is coming up next month. Don't forget to compare prices!",
        f"The weather is finally warming up in {c}! Perfect time for that walk we've been planning.",
        f"Hi {n}, just got back from the supermarket. They were out of the pasta sauce you wanted.",
        f"Note to self: Call the plumber about the kitchen sink. It's been leaking for two days.",
        f"Quick update: The dog is at the vet for a routine check. Everything looks great!",
        f"Just booked the holiday â€” so excited! Can't believe we're going to {c}.",
        f"Morning routine tip: A 10-minute walk after breakfast improves your mood and energy.",
        f"Library book reminder: Item is due back in 3 days. Renew online to avoid a fine.",
    ])

def _no_short():
    n, d, t = random.choice(NAMES), random.choice(DATES), random.choice(TIMES)
    return random.choice([
        f"Hey, are you free tonight?",
        f"Running 10 mins late, sorry!",
        f"Can you pick up milk on the way home?",
        f"Meeting rescheduled to {t}.",
        f"Happy birthday {n}! Hope you have an amazing day!",
        f"Don't forget the reservation is at {t}.",
        f"Just landed. All good!",
        f"Thanks for today â€” really helpful!",
        f"Dinner was amazing. Let's do it again soon.",
        f"Are you joining us on {d}?",
        f"Your package arrived. Picked it up for you.",
        f"Call me when you get a chance.",
        f"On my way, be there in 20.",
        f"Yes, that works. See you then!",
        f"Check your email â€” I sent the documents.",
        f"Congrats on the promotion!!",
        f"No worries, I'll cover you this time.",
        f"Kids are at school. House is so quiet!",
        f"Got your message. Will reply later.",
        f"Can we move the call to {t}?",
    ])

def _no_finance():
    a, d, n, b = random.choice(AMOUNTS), random.choice(DATES), random.choice(NAMES), random.choice(BANKS)
    return random.choice([
        f"Your {b} monthly statement for {d} is now available. Log in to view your transactions.",
        f"Transaction Confirmed: A payment of {a} has been successfully processed from your {b} account.",
        f"Direct Deposit Received: {a} has been deposited to your account. Balance updated.",
        f"Investment Update: Your portfolio gained 2.3% this month. View your full report.",
        f"Savings Milestone: Congratulations {n}! You've reached your savings goal of {a}.",
        f"Budget Alert: You've spent 80% of your dining budget this month. Review your spending.",
        f"Mortgage Reminder: Your monthly payment of {a} is due on {d}.",
        f"Tax Season Reminder: Your {b} tax documents are available for download.",
        f"Insurance Premium Notice: Your premium of {a} will be deducted on {d}.",
        f"Credit Score Update: Your credit score improved by 15 points this month.",
        f"ATM Use Abroad: Your {b} card was used at an ATM in {random.choice(CITIES)} on {d}.",
        f"Financial Planning: Free webinar on retirement savings strategies on {d}.",
    ])

def _no_event():
    n, d, c = random.choice(NAMES), random.choice(DATES), random.choice(CITIES)
    return random.choice([
        f"You're invited! {n}'s birthday party on {d} at 7 PM in {c}. RSVP by replying.",
        f"Save the date: Annual charity gala on {d} in {c}. Dress code: smart casual.",
        f"Concert Reminder: Your tickets for the event on {d} are confirmed. Doors open at 6:30 PM.",
        f"Event Update: Conference on {d} in {c} moved to a larger venue due to high demand.",
        f"Wedding Invitation: You are cordially invited to celebrate the marriage of {n} on {d}.",
        f"Community Fundraiser: Join us on {d} for a charity run in {c}. All fitness levels welcome!",
        f"Book Launch: {n} will be signing copies at the {c} bookstore on {d}.",
        f"Networking Event: Meet professionals in your industry on {d} in {c}. It's free!",
        f"Art Exhibition Opening: Preview night on {d} in {c}. Light refreshments served.",
        f"Annual General Meeting: Members requested to attend AGM on {d}. Agenda circulated in advance.",
    ])


# â”€â”€ Generator lists â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

PHISHING_GENERATORS = [
    (_ph_bank,         3000),
    (_ph_delivery,     2500),
    (_ph_account,      2500),
    (_ph_prize,        2500),
    (_ph_tax,          2500),
    (_ph_crypto,       2500),
    (_ph_job,          2000),
    (_ph_subscription, 2000),
    (_ph_inheritance,  2000),
    (_ph_tech_support, 2000),
    (_ph_short,        2500),
]

NORMAL_GENERATORS = [
    (_no_work,    3000),
    (_no_shopping,2500),
    (_no_personal,2500),
    (_no_family,  2500),
    (_no_health,  2000),
    (_no_travel,  2000),
    (_no_sports,  2000),
    (_no_food,    2000),
    (_no_tech,    2000),
    (_no_daily,   2000),
    (_no_finance, 2000),
    (_no_event,   1500),
    (_no_short,   2500),
]


def generate_rows(generators: list, label: int) -> list[dict]:
    rows = []
    for gen_fn, count in generators:
        for _ in range(count):
            rows.append({"body": gen_fn(), "label": label})
    return rows


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    clean_path   = project_root / "data" / "emails_clean.csv"

    print("Generating English phishing emails...")
    phishing_rows = generate_rows(PHISHING_GENERATORS, label=1)

    print("Generating English normal emails...")
    normal_rows = generate_rows(NORMAL_GENERATORS, label=0)

    total_new = len(phishing_rows) + len(normal_rows)
    print(f"   New phishing : {len(phishing_rows):,}")
    print(f"   New normal   : {len(normal_rows):,}")
    print(f"   Total new    : {total_new:,}")

    new_df = pd.DataFrame(phishing_rows + normal_rows)
    new_df["body"] = new_df["body"].astype(str).str.strip()
    new_df = new_df[new_df["body"] != ""]

    if clean_path.exists():
        existing = pd.read_csv(clean_path)
        print(f"\nExisting dataset : {len(existing):,} rows")
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    combined = combined.drop_duplicates(subset=["body"]).reset_index(drop=True)
    combined.to_csv(clean_path, index=False)

    print(f"Merged dataset   : {len(combined):,} rows")
    print(f"   Label 0 (normal)  : {int((combined.label==0).sum()):,}")
    print(f"   Label 1 (phishing): {int((combined.label==1).sum()):,}")
    print(f"   Saved: {clean_path}")


if __name__ == "__main__":
    main()
