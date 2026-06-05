SET NAMES utf8mb4;
INSERT INTO crop_types (crop_type_id, crop_name, crop_name_en) VALUES
  (1, '苹果', 'Apple'),
  (2, '樱桃', 'Cherry'),
  (3, '玉米', 'Corn'),
  (4, '葡萄', 'Grape'),
  (5, '柑桔', 'Citrus'),
  (6, '桃', 'Peach'),
  (7, '辣椒', 'Pepper'),
  (8, '马铃薯', 'Potato'),
  (9, '草莓', 'Strawberry'),
  (10, '番茄', 'Tomato')
ON DUPLICATE KEY UPDATE crop_name=VALUES(crop_name), crop_name_en=VALUES(crop_name_en);
