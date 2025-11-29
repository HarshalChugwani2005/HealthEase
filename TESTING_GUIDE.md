# HealthEase - Complete Testing Guide

## 🧪 Frontend Testing Instructions

### Prerequisites
1. Backend running on `http://127.0.0.1:8000`
2. Frontend running on `http://localhost:5173`
3. MongoDB connected with test hospital data
4. Valid test accounts (patient & hospital)

---

## Patient Side Testing

### Test 1: Hospital Search (GPS-based)
1. Navigate to `/patient/search`
2. **Allow** browser location permission
3. Verify GPS coordinates populate automatically
4. Click "Search Hospitals"
5. **Expected:** List of hospitals sorted by distance with:
   - Distance in km
   - Travel time estimate
   - Capacity status (color-coded)
   - Available beds/ICU/ventilators
   - Rating display
   - Specializations tags

### Test 2: Hospital Search (City-based)
1. On `/patient/search`, uncheck "Use my location (GPS)"
2. Enter city: "Delhi"
3. Select specialization: "Cardiology"
4. Check "Has ICU"
5. Click "Search Hospitals"
6. **Expected:** Filtered list of Delhi hospitals with cardiology and ICU

### Test 3: Hospital Search (Filters)
1. On search page, set:
   - Max distance: 20 km
   - Has Available Beds: checked
   - Has ICU: checked
   - Has Ventilator: checked
   - Sort by: Available Beds
2. Click "Search"
3. **Expected:** Results sorted by bed availability, all meeting filter criteria

### Test 4: Create Referral with Payment
1. From search results, click "Request Referral" on any hospital
2. Or navigate to `/patient/referral?hospital=HOSPITAL_ID`
3. On Referral page, select a hospital
4. Enter reason: "Chest pain, need cardiac evaluation"
5. Click "Proceed to Payment (₹150)"
6. **Expected:** Razorpay modal opens with:
   - Amount: ₹150
   - Pre-filled user details
7. Complete payment using Razorpay test credentials:
   - **Test Card:** 4111 1111 1111 1111
   - **CVV:** Any 3 digits
   - **Expiry:** Any future date
   - **OTP:** 123456
8. **Expected:** Success message, referral created, redirected to history

### Test 5: View Referral History
1. After creating referral, click "My Referrals" tab
2. **Expected:** List showing:
   - Hospital name
   - Referral status (pending initially)
   - Created date
   - Referral ID
   - Payment status (completed)
   - Reason displayed

### Test 6: Health Alerts
1. Navigate to `/patient/alerts`
2. **Expected:** List of active alerts:
   - Pollution alerts with AQI
   - Festival surge warnings
   - Epidemic advisories
   - Each with:
     - Severity badge (color-coded)
     - Recommendations list
     - City information
     - Alert icon

---

## Hospital Side Testing

### Test 7: Hospital Dashboard
1. Login as hospital user
2. Navigate to `/hospital/dashboard`
3. **Expected:** Dashboard showing:
   - Available beds count (real data)
   - Occupancy percentage
   - ICU & ventilator counts
   - Wallet balance
   - AI surge prediction card (if available)
   - Recent referrals list (last 5)
   - Quick action buttons

### Test 8: Capacity Management (Quick Update)
1. Navigate to `/hospital/capacity`
2. Note current "Available Beds" count
3. Click "+ 1" button
4. **Expected:** Count increases immediately
5. Refresh page
6. **Expected:** New count persists (saved to backend)
7. Click "- 1" button twice
8. **Expected:** Count decreases
9. Verify occupancy progress bar updates

### Test 9: Capacity Management (Full Update)
1. On capacity page, scroll to "Update Full Capacity" form
2. Change values:
   - Total Beds: 200
   - Available Beds: 80
   - ICU Beds: 25
   - Ventilators: 15
3. Click "Update Capacity"
4. **Expected:** Success message, all stats update instantly

### Test 10: Inventory Management (Add Item)
1. Navigate to `/hospital/inventory`
2. Click "+ Add Item"
3. Fill form:
   - Name: "Paracetamol 500mg"
   - Category: Medicines
   - Quantity: 100
   - Minimum Quantity: 20
   - Unit: "boxes"
4. Click "Add Item"
5. **Expected:** Form closes, new item appears in table

### Test 11: Inventory Management (Quick Update)
1. On inventory page, find any item
2. Click "+" button 3 times
3. **Expected:** Quantity increases by 3
4. Click "-" button once
5. **Expected:** Quantity decreases by 1
6. Verify stock status badge updates (low/medium/good)

### Test 12: Inventory Low Stock Alert
1. On inventory page, find an item
2. Click "-" until quantity ≤ minimum quantity
3. **Expected:** 
   - Status badge turns red ("Low")
   - Red alert banner appears at top with item name

### Test 13: Inventory Delete Item
1. On inventory page, click "Delete" on any item
2. Confirm deletion
3. **Expected:** Item removed from list immediately

### Test 14: Wallet & Transactions
1. Navigate to `/hospital/wallet`
2. **Expected:** Balance card displays current ₹ amount
3. Scroll to "Transaction History"
4. **Expected:** List showing:
   - Referral earnings (green +₹55.00)
   - Transaction type badges
   - Running balance after each transaction
   - Timestamps

### Test 15: Payout Request
1. On wallet page, ensure balance ≥ ₹100
2. Click "Request Payout"
3. Fill form:
   - Amount: ₹200 (or less than balance)
   - Account Holder Name: "Test Hospital Pvt Ltd"
   - Bank Account Number: "1234567890123456"
   - IFSC Code: "SBIN0001234"
4. Click "Submit Payout Request"
5. **Expected:** Success alert, request appears in "Payout Requests" section
6. Verify status shows "PENDING"

### Test 16: Referrals Management (View)
1. Navigate to `/hospital/referrals`
2. **Expected:** List of referrals with:
   - Incoming/Outgoing badges
   - Patient names
   - Status badges
   - Referral IDs
   - Payment status
   - Hospital earning (₹55.00 for accepted)

### Test 17: Referrals Management (Accept)
1. On referrals page, click "Pending" filter
2. Find an incoming pending referral
3. Click "Accept Referral"
4. **Expected:** 
   - Status changes to "ACCEPTED"
   - Green success message appears
   - Accept/Reject buttons disappear
   - Earning amount appears (₹55.00)

### Test 18: Referrals Management (Reject)
1. Find another incoming pending referral
2. Click "Reject"
3. Enter reason: "No available ICU beds"
4. Confirm
5. **Expected:** 
   - Status changes to "REJECTED"
   - Rejection reason displays below card
   - No earning amount

---

## Integration Testing

### Test 19: End-to-End Patient Flow
1. **Patient:** Login as patient
2. **Patient:** Search hospitals with GPS
3. **Patient:** Click "Request Referral" on hospital with low occupancy
4. **Patient:** Complete payment via Razorpay
5. **Patient:** Verify referral shows "PENDING" in history
6. **Hospital:** Login as the selected hospital
7. **Hospital:** Go to Referrals page
8. **Hospital:** Find the incoming referral
9. **Hospital:** Click "Accept Referral"
10. **Hospital:** Go to Wallet page
11. **Hospital:** Verify ₹55.00 credit in transactions
12. **Patient:** Refresh referral history
13. **Patient:** Verify status changed to "ACCEPTED"

### Test 20: Multi-Hospital Referral Chain
1. **Patient:** Create referral from Hospital A to Hospital B
2. **Hospital B:** Accept referral
3. **Hospital B:** Create outgoing referral from B to Hospital C
4. **Hospital C:** Accept referral
5. **Verify:** 
   - Hospital A and B each earned ₹55
   - Patient paid ₹150 total
   - All statuses updated correctly

### Test 21: Capacity Update Reflects in Search
1. **Hospital:** Login as hospital
2. **Hospital:** Update available beds to 5
3. **Patient:** Login as patient
4. **Patient:** Search hospitals
5. **Patient:** Find the hospital
6. **Expected:** Available beds shows 5, occupancy recalculated

### Test 22: Low Inventory Alert Workflow
1. **Hospital:** Set item quantity ≤ minimum
2. **Hospital:** Verify red alert banner appears
3. **Hospital:** Click "+" to increase quantity above minimum
4. **Hospital:** Verify alert disappears

---

## Edge Cases & Error Handling

### Test 23: Payment Cancellation
1. **Patient:** Create referral, open Razorpay
2. **Patient:** Click "X" to close modal (cancel)
3. **Expected:** Error message "Payment cancelled"
4. **Verify:** No referral created, no money charged

### Test 24: Insufficient Wallet Balance
1. **Hospital:** Request payout for full balance
2. **Hospital:** Try requesting another payout immediately
3. **Expected:** Button disabled (balance < ₹100)

### Test 25: GPS Permission Denied
1. **Patient:** Block location permission
2. **Patient:** Go to search page
3. **Expected:** 
   - Error message appears
   - "Use my location" auto-unchecks
   - City search mode activates

### Test 26: Invalid Search Filters
1. **Patient:** Check all filters (beds, ICU, ventilator)
2. **Patient:** Set max distance to 1 km
3. **Patient:** Search
4. **Expected:** "No hospitals found" message if criteria too strict

### Test 27: Delete Active Inventory Item
1. **Hospital:** Create item, then delete
2. **Hospital:** Try updating deleted item
3. **Expected:** Item no longer appears, API returns 404

---

## Performance Testing

### Test 28: Large Dataset
1. Create 50+ hospitals in database
2. **Patient:** Search without filters
3. **Expected:** Page loads within 2 seconds, all results render

### Test 29: Real-time Updates
1. Open hospital dashboard in 2 browser tabs
2. In Tab 1: Update capacity
3. In Tab 2: Refresh page
4. **Expected:** Tab 2 shows updated capacity

### Test 30: Concurrent Referrals
1. Create 5 referrals simultaneously from different patients
2. **Hospital:** View referrals page
3. **Expected:** All 5 appear correctly without data loss

---

## Mobile Responsiveness

### Test 31: Mobile Search
1. Open `/patient/search` on mobile viewport (375px)
2. **Expected:** 
   - Grid changes to single column
   - Buttons stack vertically
   - Filters remain accessible
   - Cards responsive

### Test 32: Mobile Referrals
1. Open `/hospital/referrals` on mobile
2. **Expected:** 
   - Cards stack vertically
   - Accept/Reject buttons full width
   - All info readable

---

## Security Testing

### Test 33: Unauthorized Access
1. Logout completely
2. Try accessing `/hospital/dashboard` directly
3. **Expected:** Redirect to login or 401 error

### Test 34: Role-Based Access
1. Login as patient
2. Try accessing `/hospital/inventory`
3. **Expected:** 403 forbidden or redirect

### Test 35: API Token Expiry
1. Login, wait for token expiry (7 days)
2. Try any API call
3. **Expected:** 401 Unauthorized, redirect to login

---

## Checklist Summary

| Test # | Feature | Status |
|--------|---------|--------|
| 1-3 | Patient Search (GPS/City/Filters) | ⬜ |
| 4 | Referral with Payment | ⬜ |
| 5 | Referral History | ⬜ |
| 6 | Health Alerts | ⬜ |
| 7 | Hospital Dashboard | ⬜ |
| 8-9 | Capacity Management | ⬜ |
| 10-13 | Inventory Management | ⬜ |
| 14-15 | Wallet & Payouts | ⬜ |
| 16-18 | Referrals Management | ⬜ |
| 19-22 | Integration Tests | ⬜ |
| 23-27 | Edge Cases | ⬜ |
| 28-30 | Performance | ⬜ |
| 31-32 | Mobile Responsiveness | ⬜ |
| 33-35 | Security | ⬜ |

---

## Test Data Setup

### Create Test Hospital
```bash
POST /api/auth/register
{
  "email": "test.hospital@healthease.com",
  "password": "Test@1234",
  "name": "Test General Hospital",
  "role": "hospital",
  "hospital_details": {
    "address": "123 Test Street",
    "city": "Delhi",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "phone": "9876543210",
    "specializations": ["Cardiology", "Neurology"]
  }
}
```

### Create Test Patient
```bash
POST /api/auth/register
{
  "email": "test.patient@healthease.com",
  "password": "Test@1234",
  "name": "Test Patient",
  "role": "patient"
}
```

---

## Razorpay Test Credentials

**Test Mode API Keys (already configured in backend):**
- Key ID: `rzp_test_...`
- Key Secret: `...`

**Test Card Details:**
- Card Number: `4111 1111 1111 1111`
- CVV: `123`
- Expiry: `12/25`
- OTP: `123456`

**Test UPI:**
- UPI ID: `success@razorpay`
- Status: Auto-approved

---

## Bug Reporting Template

```
**Test #:** [number]
**Page:** [URL]
**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**

**Actual Behavior:**

**Console Errors:** [paste]
**Network Response:** [paste]
**Screenshots:** [attach]
```

---

## Success Criteria

✅ All 35 tests pass
✅ No console errors
✅ Mobile responsive (375px - 1920px)
✅ Load time < 3 seconds
✅ No data loss on refresh
✅ Payment flow completes successfully
✅ Real-time updates work

---

*Last Updated: November 29, 2025*
*Test Coverage: 8 Pages | 26 APIs | 35 Test Cases*
