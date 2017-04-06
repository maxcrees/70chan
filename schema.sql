-- Tables ----------------------------------------------------------------------

-- Boards table
CREATE TABLE "boards" (
  `name`  TEXT NOT NULL UNIQUE,
  `description` TEXT,
  `posts` INTEGER NOT NULL DEFAULT 0,
  `threads` INTEGER NOT NULL DEFAULT 0,
  `ts`  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Posts table
CREATE TABLE "posts" (
  `board` TEXT NOT NULL,                              -- board name
  `thread`  INTEGER NOT NULL,                         -- indicates ID of original post this post is in reply to (0 if this post is original)
  `tdate` TEXT,                                       -- date of last reply in this thread (set only if thread == 0)
  `tword` TEXT,                                       -- URL slug of this thread (set only if thread == 0)
  `replies` INTEGER NOT NULL DEFAULT 0,               -- number of replies (threads only)
  `id`  INTEGER NOT NULL,                             -- post ID
  `author`  TEXT NOT NULL DEFAULT 'Anonymous',        -- author name
  `ip`  TEXT,                                         -- author IP address
  `ts`  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,      -- post date
  `text`  TEXT NOT NULL,                              -- post body
  `deleted` INTEGER NOT NULL DEFAULT 0,               -- if deleted == 1, hide this post's content from users
  `imageext`  TEXT,                                   -- image filename extension, with period (leave blank if no image attached)
  `imagename` TEXT                                    -- original image filename from poster's computer (leave blank if no image)
);
-- Bans table
CREATE TABLE "bans" (
  `board` TEXT,                                       -- (optional) limit ban to specific board
  `ip`  TEXT NOT NULL,                                -- poster's IP address
  `reason`  TEXT NOT NULL DEFAULT '(no reason given)' -- reason for ban
);

-- Triggers --------------------------------------------------------------------

-- Prevent creation of posts in boards that do not exist
CREATE TRIGGER check_board_name BEFORE INSERT ON posts
WHEN NOT EXISTS(SELECT name FROM boards WHERE name = NEW.board)
BEGIN
  SELECT RAISE(ROLLBACK, 'That board does not exist!');
END;
-- Prevent creation of posts with non-unique IDs
CREATE TRIGGER check_post_id BEFORE INSERT ON posts
WHEN EXISTS(SELECT id FROM posts WHERE id = NEW.id AND board = NEW.board)
BEGIN
  SELECT RAISE(ROLLBACK, 'That post already exists!');
END;
-- Prevent creation of posts with non-unique thread words
CREATE TRIGGER check_post_word BEFORE INSERT ON posts
WHEN EXISTS(SELECT tword FROM posts WHERE tword = NEW.tword AND board = NEW.board)
BEGIN
  SELECT RAISE(ROLLBACK, 'That post already exists!');
END;
-- Update posts count in boards table
CREATE TRIGGER update_post_count AFTER INSERT ON posts
WHEN EXISTS(SELECT name FROM boards WHERE name = NEW.board)
BEGIN
  UPDATE boards SET posts = posts + 1 WHERE name = NEW.board;
END;
-- Update thread count in boards table
CREATE TRIGGER update_thread_count AFTER INSERT ON posts
WHEN NEW.thread = 0 AND EXISTS(SELECT name FROM boards WHERE name = NEW.board)
BEGIN
  UPDATE boards SET threads = threads + 1 WHERE name = NEW.board;
END;
-- Update thread last reply date and reply count in posts table
CREATE TRIGGER update_thread AFTER INSERT ON posts
WHEN NEW.thread != 0 AND EXISTS(SELECT id FROM posts WHERE id = NEW.thread AND thread = 0 AND board = NEW.board)
BEGIN
  UPDATE posts SET tdate = NEW.ts, replies = replies + 1 WHERE id = NEW.thread AND thread = 0 AND board = NEW.board;
END;
-- Update board timestamp
CREATE TRIGGER update_board_date AFTER INSERT ON posts
WHEN EXISTS(SELECT name FROM boards WHERE name = NEW.board)
BEGIN
  UPDATE boards SET ts = NEW.ts WHERE name = NEW.board;
END;
