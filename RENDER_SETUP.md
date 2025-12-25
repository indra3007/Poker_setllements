# Render Deployment Setup Guide

## Important: Database Configuration

### Security Notice

For security reasons, the database credentials are **NOT** stored in `render.yaml`. You must configure the `DATABASE_URL` environment variable manually in the Render Dashboard.

### Steps to Configure DATABASE_URL in Render

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com/
   - Navigate to your `poker-tracker` web service

2. **Add Environment Variable**
   - Click on the service name
   - Go to the "Environment" tab
   - Click "Add Environment Variable"

3. **Set DATABASE_URL**
   - **Key**: `DATABASE_URL`
   - **Value**: 
     ```
     postgresql://poker_settlements_user:39d1mKqYkt252OAVwEfFFK1vDnPuIEWN@dpg-d56rrvre5dus73cvg310-a/poker_settlements
     ```

4. **Save and Redeploy**
   - Click "Save Changes"
   - Render will automatically redeploy your service
   - The application will now use the PostgreSQL database

### Verification

After deployment, check the logs to verify database connection:

```
🔗 Database Configuration:
==================================================
DATABASE_URL is configured: True
Initializing database schema...
✅ Database initialized successfully!
==================================================
```

### Troubleshooting

If you see database connection errors:

1. **Verify DATABASE_URL is set correctly in Render Dashboard**
   - Check spelling and format
   - Ensure no extra spaces

2. **Check database service status**
   - Verify the PostgreSQL database is running on Render

3. **Fallback behavior**
   - If database connection fails, the app will fall back to file-based storage
   - Application will continue to function normally
   - Error messages will appear in logs

### Alternative: Using render.yaml (Not Recommended)

If you prefer to use render.yaml (not recommended for security), you can:

1. Uncomment the DATABASE_URL value in render.yaml
2. Add the actual connection string
3. **Never commit this to public repositories**

However, the recommended approach is to use the Render Dashboard's environment variable management.

## Local Development

For local development:

1. Copy `.env.example` to `.env`
2. Update the `DATABASE_URL` with your local PostgreSQL connection string
3. The application will automatically load it

Example `.env`:
```
DATABASE_URL=postgresql://localhost:5432/poker_tracker_dev
```

## Database Credentials Reference

Keep these credentials secure and only use them where needed:

- **Username**: `poker_settlements_user`
- **Password**: `39d1mKqYkt252OAVwEfFFK1vDnPuIEWN`
- **Host**: `dpg-d56rrvre5dus73cvg310-a`
- **Database**: `poker_settlements`
- **Connection String**: `postgresql://poker_settlements_user:39d1mKqYkt252OAVwEfFFK1vDnPuIEWN@dpg-d56rrvre5dus73cvg310-a/poker_settlements`

**IMPORTANT**: 
- Do not commit these credentials to version control
- Do not share these credentials publicly
- Only use them in secure environment variable configurations
