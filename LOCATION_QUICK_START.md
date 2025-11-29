# Quick Start - Location Detection

## No Google API Key? No Problem!

The app will work with the free IP-based location service by default. Here's how to get started:

### Option 1: Quick Test (No API Key Required)

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the app:**
   - Navigate to Patient Dashboard → Search Hospitals
   - Enable "Use my location (GPS)"
   - Allow browser location permission when prompted
   - If browser permission is denied, the app will automatically use IP-based location

**Expected Result:** Hospitals will appear based on your approximate location (city-level accuracy).

---

### Option 2: With Google API Key (Recommended for Production)

For better accuracy, follow the [GOOGLE_MAPS_SETUP.md](./GOOGLE_MAPS_SETUP.md) guide to:
1. Create a Google Cloud project
2. Enable Geolocation API
3. Get an API key
4. Add it to your `.env` files:

**Backend (.env):**
```env
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

**Frontend (.env):**
```env
VITE_GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

5. Restart both servers

---

## Testing Location Detection

### Scenario 1: Browser GPS Permission Granted ✅
- **Expected:** Most accurate location (within 10-100 meters)
- **Result:** Hospitals sorted by actual distance from your location

### Scenario 2: Browser GPS Permission Denied ❌
- **Expected:** Falls back to Google API or IP-based location
- **Result:** Hospitals sorted by approximate location (city-level)

### Scenario 3: Testing on Localhost
- **Expected:** May show default location (Delhi, India)
- **Solution:** 
  - Use a real IP address
  - Deploy to a staging server
  - Or test with Google API key enabled

---

## Troubleshooting

### "No hospitals found"
**Problem:** Location detected but no results  
**Solutions:**
1. Increase "Max Distance" to 100 km
2. Uncheck filter options (Available Beds, ICU, etc.)
3. Make sure hospitals in database have location coordinates
4. Try city-based search instead

### "Location detection failed"
**Problem:** All location methods failed  
**Solutions:**
1. Check browser console for specific errors
2. Try a different browser
3. Clear browser cache and cookies
4. Manually enter your city name

### Hospitals not sorted by distance
**Problem:** Results appear but distances seem wrong  
**Solutions:**
1. Verify location coordinates are correct (check the green status box)
2. Ensure hospitals in database have valid coordinates
3. Try refreshing the page and detecting location again

---

## Database Setup Note

For location-based search to work, hospitals in your database must have:

```json
{
  "location": {
    "type": "Point",
    "coordinates": [longitude, latitude]
  }
}
```

**Example:**
```json
{
  "name": "City Hospital",
  "location": {
    "type": "Point",
    "coordinates": [77.2090, 28.6139]  // Delhi coordinates
  }
}
```

If your database doesn't have location data, see [DATABASE_SETUP.md](./backend/DATABASE_SETUP.md) for instructions on adding it.

---

## Production Deployment

When deploying to production:

1. **Use HTTPS** - Browser geolocation requires it
2. **Add domain to Google API restrictions** 
3. **Set environment variables** on your hosting platform
4. **Enable CORS** for your production domain
5. **Monitor API usage** in Google Cloud Console

---

## Cost Summary

- **Without Google API:** 100% free, city-level accuracy
- **With Google API:** $200/month free credit, better accuracy
  - Geolocation API: 40,000 free requests/month
  - Typical usage: ~100-500 requests/day
  - **Expected cost:** $0 (within free tier)

For most applications, you'll never need to pay for the API.
