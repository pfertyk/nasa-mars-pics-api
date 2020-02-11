create table mars_image (
	url text PRIMARY KEY,
	sol integer,
	width integer,
	height integer,
	mode text,
	approved boolean default true
);
