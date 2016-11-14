head' :: [a] -> a 
head' (x : xs) = x

tail' :: [a] -> [a]
tail' [] = []
tail' (x : xs) = xs

take' :: Int -> [a] -> [a]
take' 0 xs = []
take' left [] = []
take' left (x : xs) = x : take' (left - 1) xs

drop' :: Int -> [a] -> [a]
drop' 0 l = l
drop' left [] = []
drop' left (x : xs) = drop' (left - 1) xs

filter' :: (a -> Bool) -> [a] -> [a]
filter' f [] = [] 
filter' f (x : xs) = if f x
              then x : filter' f xs
              else filter' f xs

foldl' :: (a -> b -> a) -> a -> [b] -> a
foldl' f z [] = z
foldl' f z (x : xs) = foldl' f (f z x) xs 

concat' :: [a] -> [a] -> [a]
concat' [] l = l
concat' (x : xs) l = x : concat' xs l

quickSort' :: Ord a => [a] -> [a]
quickSort' [] = []
quickSort' (x : []) = x : []
quickSort' (x : l) = concat' (quickSort' (filter' (<= x) l))  (x : (quickSort' (filter' (> x) l))) 
