# PostgreSQL Database Integration

## Overview

The Poker Tracker application has been updated to integrate PostgreSQL database for persistent data storage. The application now supports database-backed storage while maintaining backward compatibility with file-based storage (JSON/Excel).

## Features

### Database Schema

The application uses three main tables:

1. **events** - Stores poker event/session information
   - `id`: Auto-incrementing primary key
   - `event_name`: Unique event identifier
   - `created_at`: Timestamp of event creation

2. **players** - Stores player data for each event
   - `id`: Auto-incrementing primary key
   - `event_name`: Foreign key referencing events table
   - `name`: Player name
   - `phone`: Player phone number
   - `start_chips`: Starting chip count (default: 20)
   - `buyins`: Number of buy-ins
   - `day1-day7`: Chip counts for each day
   - `pl`: Profit/Loss calculation
   - `days_played`: Number of days participated

3. **settlement_payments** - Tracks settlement payment status
   - `id`: Auto-incrementing primary key
   - `event_name`: Foreign key referencing events table
   - `from_player`: Player making payment
   - `to_player`: Player receiving payment
   - `paid`: Boolean flag indicating payment status

### Configuration

#### Environment Variables

Set the `DATABASE_URL` environment variable to your PostgreSQL connection string:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

For local development:
1. Copy `.env.example` to `.env`
2. Update the `DATABASE_URL` with your local PostgreSQL credentials
3. The application will automatically load environment variables from `.env`

For production (Render platform):
- The `DATABASE_URL` is automatically set in `render.yaml`
- Render will use the provided PostgreSQL credentials

#### Fallback Behavior

The application intelligently handles database connectivity:

- **When DATABASE_URL is set and database is accessible:**
  - Primary storage: PostgreSQL database
  - Secondary storage: JSON/Excel files (for backup/compatibility)

- **When DATABASE_URL is not set or database is unavailable:**
  - Falls back to file-based storage (JSON/Excel)
  - Application continues to function normally
  - Error messages are logged but don't disrupt service

### API Endpoints

All existing API endpoints continue to work with no changes:

- `GET /api/events` - List all events
- `POST /api/events` - Create new event
- `DELETE /api/events/<event_name>` - Delete an event
- `GET /api/data/<event_name>` - Get player data for an event
- `POST /api/save/<event_name>` - Save player data
- `GET /api/settlements/<event_name>` - Calculate settlements
- `POST /api/settlements/<event_name>/mark_paid` - Mark settlement as paid
- `POST /api/clear/<event_name>` - Clear event data

### Error Handling

The application includes comprehensive error handling:

1. **Connection Errors**: Logged and triggers fallback to file storage
2. **Database Query Errors**: Caught and reported with fallback
3. **Network Issues**: Handled gracefully with continued operation

Example error handling flow:
```python
try:
    # Attempt database operation
    result = db_load_events()
except Exception as e:
    # Log error
    print(f"Database error, falling back to JSON: {e}")
    # Fall through to file-based storage
    result = load_from_json()
```

## Installation

### Dependencies

The following packages are required:

```
Flask==3.0.0
openpyxl==3.1.5
Werkzeug==3.0.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

### Local Development

1. Set up PostgreSQL database
2. Create `.env` file with `DATABASE_URL`
3. Run the application:
   ```bash
   python app.py
   ```
4. The application will:
   - Initialize database schema if needed
   - Fall back to file storage if database unavailable
   - Start on port 5001 by default

### Production Deployment (Render)

The application is configured for deployment on Render:

1. Push changes to GitHub
2. Render automatically:
   - Installs dependencies from `requirements.txt`
   - Sets `DATABASE_URL` from `render.yaml`
   - Initializes database schema on first run
   - Starts the application with Gunicorn

## Testing

A comprehensive test suite is provided in `test_database.py`:

```bash
python test_database.py
```

This tests:
- Event creation and retrieval
- Player data operations
- Settlement calculations
- Payment tracking
- Database fallback behavior
- Error handling

## Migration Notes

### From File-Based to Database

When migrating existing data:

1. **Events**: Existing events in `events.json` will continue to work
2. **Player Data**: Excel files provide backup/compatibility
3. **Settlements**: `settlements_tracking.json` serves as fallback
4. **No Data Loss**: Dual storage ensures data persistence

### Backward Compatibility

The application maintains full backward compatibility:
- Works with or without database
- Existing JSON/Excel files remain functional
- No breaking changes to API
- Frontend requires no modifications

## Security Considerations

### Credentials Management

**IMPORTANT**: Never commit database credentials to version control.

- ✅ Use environment variables for `DATABASE_URL`
- ✅ `.env` file is in `.gitignore`
- ✅ Production credentials set in deployment platform
- ✅ `.env.example` provides template without sensitive data

### Connection Security

- Uses PostgreSQL's built-in connection encryption
- Credentials passed securely through environment
- No plaintext passwords in code

### SQL Injection Prevention

- All queries use parameterized statements
- User input is properly sanitized
- psycopg2 handles escaping automatically

## Monitoring

### Database Health

Monitor database connectivity with startup logs:
```
🔗 Database Configuration:
==================================================
DATABASE_URL is configured: True
Initializing database schema...
✅ Database initialized successfully!
==================================================
```

### Error Logs

Watch for database errors in application logs:
```
❌ Database error, falling back to JSON: [error message]
```

These indicate temporary connectivity issues but application continues functioning.

## Troubleshooting

### Database Connection Fails

**Symptom**: Application logs show connection errors

**Solution**:
1. Verify `DATABASE_URL` is correctly set
2. Check database host is accessible
3. Confirm credentials are correct
4. Application will use file fallback automatically

### Schema Initialization Fails

**Symptom**: Tables don't exist errors

**Solution**:
1. Restart application to re-run initialization
2. Manually create schema using `database.py`
3. Check database permissions

### Data Not Persisting

**Symptom**: Data disappears after restart

**Solution**:
1. Check if `DATABASE_URL` is set in production
2. Verify database service is running
3. Check application logs for errors
4. Fallback files should still have data

## Performance

### Database vs File Storage

- **Database**: Better for concurrent access, multiple users
- **File Storage**: Sufficient for single-user, local use
- **Hybrid**: Best of both worlds with fallback

### Query Optimization

- Indexes on foreign keys improve performance
- Connection pooling via psycopg2
- Minimal query overhead

## Future Enhancements

Potential improvements:
1. Connection pooling for better performance
2. Database migrations system (Alembic)
3. Read replicas for scaling
4. Backup/restore utilities
5. Data import/export tools

## Support

For issues or questions:
1. Check application logs for error details
2. Verify environment configuration
3. Test database connectivity separately
4. Review this documentation

## References

- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Render PostgreSQL Guide](https://render.com/docs/databases)
