# Proposed cache

The service currently reads directly from the primary database. The proposed
in-memory cache would use a 30-second TTL. There is no event-driven
invalidation design yet.

Product requirements allow up to 60 seconds of staleness for catalog reads but
require current values for account balances. The proposal does not separate
these two data classes.
