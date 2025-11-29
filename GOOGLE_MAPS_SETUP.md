# Google Maps API Setup Guide

## Getting Your Google Maps API Key

### Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top
4. Click "New Project"
5. Enter a project name (e.g., "HealthEase")
6. Click "Create"

### Step 2: Enable Required APIs
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - **Geolocation API** (Required for location detection)
   - **Maps JavaScript API** (Optional, for future map features)
   - **Geocoding API** (Optional, for address conversion)

### Step 3: Create API Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key
4. Click "Edit API key" (recommended)
5. Under "API restrictions", select "Restrict key"
6. Select the APIs you enabled (Geolocation API, etc.)
7. Under "Application restrictions" (optional but recommended):
   - For development: Select "HTTP referrers" and add:
     - `http://localhost:*`
     - `http://127.0.0.1:*`
   - For production: Add your production domain
8. Click "Save"

### Step 4: Configure Your Application

#### Backend (.env file)
```bash
GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE
```

#### Frontend (.env file)
```bash
VITE_GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE
```

### Step 5: Enable Billing (Required)
Google requires billing to be enabled for the Geolocation API, but offers:
- $200 free monthly credit
- Free tier for most usage levels
- You won't be charged unless you exceed the free quota

To enable billing:
1. Go to "Billing" in Google Cloud Console
2. Click "Link a billing account" or "Create billing account"
3. Enter your payment information

## Location Detection Flow

The application now uses a three-tier fallback system:

### Tier 1: Browser Geolocation API (Primary)
- **Pros**: Fast, accurate, free
- **Cons**: Requires HTTPS in production, user permission
- **Used when**: User grants location permission

### Tier 2: Google Geolocation API (Fallback)
- **Pros**: Works without user permission, good accuracy
- **Cons**: Requires API key, has usage limits
- **Used when**: Browser API fails or is denied

### Tier 3: IP-based Geolocation (Last Resort)
- **Pros**: Always works, no setup needed
- **Cons**: Less accurate (city-level)
- **Used when**: Both other methods fail

## Testing Your Setup

1. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test location detection:**
   - Go to the Patient Dashboard > Search page
   - Check the "Use my location (GPS)" checkbox
   - You should see one of these:
     - ✅ "Location detected: [coordinates]" (success)
     - 🔄 "Detecting your location..." (in progress)
     - ⚠️ Error message with fallback explanation

4. **Verify hospitals appear:**
   - After location is detected, hospitals should automatically load
   - Check browser console for any errors
   - Verify the API key is being sent in requests

## Troubleshooting

### "Location detection failed"
- **Solution 1**: Make sure you've added the API key to both `.env` files
- **Solution 2**: Restart both frontend and backend servers
- **Solution 3**: Check browser console for specific error messages

### "Google API error"
- **Solution 1**: Verify the API key is correct
- **Solution 2**: Ensure Geolocation API is enabled in Google Cloud
- **Solution 3**: Check if billing is enabled

### "No hospitals found"
- **Solution 1**: Try increasing the "Max Distance" setting
- **Solution 2**: Check if hospitals have location coordinates in the database
- **Solution 3**: Try city-based search instead of GPS

### HTTPS Required (Production)
- Browser Geolocation API requires HTTPS in production
- Use services like Netlify, Vercel, or configure SSL on your server

## Security Best Practices

1. **Never commit API keys to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Restrict API key usage**
   - Set HTTP referrer restrictions
   - Limit to specific APIs
   - Monitor usage in Google Cloud Console

3. **Set up usage quotas**
   - Configure alerts for high usage
   - Set daily quotas to prevent unexpected charges

## Cost Estimation

With the free tier:
- **Geolocation API**: Free for first 40,000 requests/month
- **Maps JavaScript API**: Free for first 28,000 loads/month
- **Typical usage**: ~100-500 requests/day = well within free tier

For a small to medium application, you'll likely stay within the free tier indefinitely.

## Alternative: Free IP-Based Location (No API Key)

If you don't want to use Google's paid services, the app will automatically fall back to free IP-based geolocation using ipapi.co, which provides:
- City-level accuracy
- No API key required
- 1,000 free requests/day per IP

This is less accurate but sufficient for basic hospital search functionality.
