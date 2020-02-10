create table mars_image (
	url text PRIMARY KEY,
	width integer,
	height integer,
	mode text,
	approved boolean default true
);
