CineGuard — All Options Implemented
-----------------------------------

This package implements all five seat-mapping options:
1) Seat types (premium/normal/economy) with pricing.
2) Multiple screen layouts including curved rows and sectioned (PVR) layout.
3) Hover animation and popup seat info.
4) Multiple screens selectable from the UI.
5) Complex theatre sections (Left/Center/Right) and a VIP screen.

Files:
- index.html      : User booking UI with advanced seat mapping.
- admin.php       : Admin panel with camera preview and bookings list.
- config.php      : PDO DB config (update credentials).
- book_seat.php   : Booking endpoint (POST seat,type,price,name,phone).
- fetch_bookings.php : Returns all bookings in JSON.
- database.sql    : SQL schema + sample rows.

Setup:
1. Import database.sql into MySQL.
   mysql -u root -p < database.sql
2. Update config.php DB credentials as needed.
3. Deploy files to a PHP-enabled web server.

Notes:
- Camera & detection in admin are placeholders. For ML detection integration,
  send frames to a server-side model and map detections to seats (I can help).
- Seat IDs in PVR layout include suffixes (-L, -C, -R) to disambiguate sections.

If you'd like, I can:
- Add admin authentication.
- Map detected coordinates to specific seats (requires camera calibration).
- Add seat selection by price filter or seat search.
