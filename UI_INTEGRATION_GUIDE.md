# 📞 Calling Feature - UI Integration Guide

## Where to Add the Calling Components

This guide shows you exactly where to integrate the calling feature components in your LegalConnect application.

---

## 1️⃣ **User Profile Page - Call Button**

### Location: User Profile / Advocate Card

**Before:**
```
┌─────────────────────────────────────┐
│  👤 Advocate Name                   │
│  ⭐ Verified Advocate               │
│  📧 advocate@example.com            │
│                                     │
│  Bio: Experienced lawyer...         │
│                                     │
│  [Follow] [Message]                 │  ← Only Follow and Message
│                                     │
│  Followers: 150 | Following: 45     │
└─────────────────────────────────────┘
```

**After (With Call Button):**
```
┌─────────────────────────────────────┐
│  👤 Advocate Name                   │
│  ⭐ Verified Advocate               │
│  📧 advocate@example.com            │
│                                     │
│  Bio: Experienced lawyer...         │
│                                     │
│  [Follow] [Message] [📞 Call]       │  ← NEW: Call button added
│                                     │
│  💰 Wallet: ₹100                    │  ← NEW: Wallet balance
│  Followers: 150 | Following: 45     │
└─────────────────────────────────────┘
```

**Code to Add:**
```jsx
// In your Profile.js or UserCard.js component
import CallButton from './components/CallButton';

// Inside the component JSX, after Follow and Message buttons:
{user.role === 'Advocate' && (
  <CallButton 
    currentUserId={currentUser.id}
    targetUserId={user.id}
    targetUserName={user.name}
    targetUserRole={user.role}
  />
)}

// Display wallet balance
<div className="wallet-display">
  💰 Wallet: ₹{currentUser.wallet_balance || 0}
</div>
```

---

## 2️⃣ **User Dashboard - Call History**

### Location: User Dashboard / My Account Page

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  My Dashboard                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Profile Info                                           │
│  ├─ Name: John Doe                                     │
│  ├─ Email: john@example.com                            │
│  └─ Wallet Balance: ₹100                               │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  📞 Call History                    ← NEW SECTION       │
│                                                         │
│  ┌─────────────┬─────────────┐                         │
│  │ Total Calls │ Total Spent │                         │
│  │     5       │    ₹100     │                         │
│  └─────────────┴─────────────┘                         │
│                                                         │
│  Recent Calls:                                          │
│  ┌───────────────────────────────────────────┐         │
│  │ 📤 Outgoing | Jan 25, 11:00 AM            │         │
│  │ Duration: 10m | Amount: ₹20 | ✅ Completed│         │
│  └───────────────────────────────────────────┘         │
│                                                         │
│  ┌───────────────────────────────────────────┐         │
│  │ 📥 Incoming | Jan 24, 3:30 PM             │         │
│  │ Duration: 8m | Amount: ₹20 | ✅ Completed │         │
│  └───────────────────────────────────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Code to Add:**
```jsx
// In your Dashboard.js component
import CallHistory from './components/CallHistory';

// Inside the dashboard JSX:
<section className="call-history-section">
  <CallHistory userId={currentUser.id} />
</section>
```

---

## 3️⃣ **Admin Panel - Call Settings**

### Location: Admin Dashboard / Settings

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  ⚙️ Admin Panel                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Call Feature Settings              ← NEW SECTION       │
│                                                         │
│  Statistics Dashboard:                                  │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │ 📞 Total │ 💰 Revenue│ ✅ Done  │ 🔴 Active│         │
│  │   150    │  ₹3,000  │   145    │    5     │         │
│  └──────────┴──────────┴──────────┴──────────┘         │
│                                                         │
│  Configuration:                                         │
│  ┌─────────────────────────────────────────┐           │
│  │ Call Price (₹):      [20]               │           │
│  │ Call Duration (min): [10]               │           │
│  │ ☑️ Enable Calling Feature               │           │
│  │                                         │           │
│  │ [Save Settings]                         │           │
│  └─────────────────────────────────────────┘           │
│                                                         │
│  Recent Calls:                                          │
│  ┌─────────────────────────────────────────┐           │
│  │ Date      │ Caller │ Receiver │ Amount  │           │
│  ├───────────┼────────┼──────────┼─────────┤           │
│  │ Jan 25    │ user1  │ user2    │ ₹20     │           │
│  │ Jan 25    │ user3  │ user4    │ ₹20     │           │
│  └─────────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Code to Add:**
```jsx
// In your AdminDashboard.js component
import AdminCallSettings from './components/AdminCallSettings';

// Inside the admin panel JSX:
{currentUser.role === 'Admin' && (
  <section className="admin-call-settings">
    <AdminCallSettings adminId={currentUser.id} />
  </section>
)}
```

---

## 4️⃣ **Active Call Interface (Overlay)**

### When a Call is Active

**Full-Screen Overlay:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                                                         │
│              📞 Calling                                 │
│         Advocate Name                                   │
│                                                         │
│                                                         │
│              ⏱️  09:45                                  │
│              remaining                                  │
│                                                         │
│         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░                          │
│         Progress Bar                                    │
│                                                         │
│                                                         │
│           [  End Call  ]                                │
│                                                         │
│                                                         │
│      💰 This call costs ₹20 for 10 minutes             │
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**This appears automatically when call starts - no code needed!**

---

## 5️⃣ **Payment Confirmation Modal**

### When User Clicks Call Button

**Modal Popup:**
```
        ┌─────────────────────────────────┐
        │  Confirm Call Payment      [×]  │
        ├─────────────────────────────────┤
        │                                 │
        │  Calling: Advocate Name         │
        │  Duration: 10 minutes           │
        │  Price: ₹20                     │
        │                                 │
        │  ─────────────────────────────  │
        │                                 │
        │  Your Balance: ₹100             │
        │  After Call: ₹80                │
        │                                 │
        │  ─────────────────────────────  │
        │                                 │
        │  [Cancel]  [Confirm & Pay]      │
        │                                 │
        └─────────────────────────────────┘
```

**This appears automatically when CallButton is clicked - no code needed!**

---

## 📝 **Quick Integration Checklist**

### Step 1: Find Your Profile Component
- [ ] Locate `Profile.js` or `UserCard.js` or similar
- [ ] Import `CallButton` component
- [ ] Add `<CallButton />` after Follow/Message buttons
- [ ] Add wallet balance display

### Step 2: Find Your Dashboard Component
- [ ] Locate `Dashboard.js` or `MyAccount.js`
- [ ] Import `CallHistory` component
- [ ] Add `<CallHistory />` in a new section

### Step 3: Find Your Admin Panel
- [ ] Locate `AdminDashboard.js` or `Admin.js`
- [ ] Import `AdminCallSettings` component
- [ ] Add `<AdminCallSettings />` in admin panel

### Step 4: Test
- [ ] Login as Public user
- [ ] View an Advocate profile
- [ ] See Call button (may be disabled if no mutual follow)
- [ ] Follow the Advocate (and have them follow back)
- [ ] Call button should become enabled
- [ ] Click Call → See payment modal
- [ ] Confirm payment → See call interface

---

## 🎨 **Visual States**

### Call Button States:

**Enabled (Mutual Follow + Sufficient Balance):**
```
[📞 Call]  ← Green, clickable
```

**Disabled (No Mutual Follow):**
```
[📞 Call]  ← Gray, with tooltip:
           "Both users must follow each other to enable calling"
```

**Disabled (Insufficient Balance):**
```
[📞 Call]  ← Gray, with tooltip:
           "Insufficient balance. Required: ₹20, Available: ₹5"
```

---

## 🔗 **Component Props Reference**

### CallButton
```jsx
<CallButton 
  currentUserId="user123"        // Current logged-in user
  targetUserId="user456"         // User to call
  targetUserName="Advocate Name" // Display name
  targetUserRole="Advocate"      // Must be "Advocate"
/>
```

### CallHistory
```jsx
<CallHistory 
  userId="user123"  // User whose history to show
/>
```

### AdminCallSettings
```jsx
<AdminCallSettings 
  adminId="admin001"  // Admin user ID
/>
```

---

## ✅ **You're All Set!**

Once you integrate these components, users will see:
- 📞 Call buttons on Advocate profiles
- 💰 Wallet balances
- 📊 Call history in dashboard
- ⚙️ Admin controls for pricing

**The feature is fully functional and ready to use!** 🎉
