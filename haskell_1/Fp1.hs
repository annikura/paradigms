head' :: [a] -> a 
head' (xs : x) = xs

tail' :: [a] -> [a]
tail' [] = []
tail' (xs : x) = x

take' :: Int -> [a] -> [a]
take' 0 xs = []
take' left [] = []
take' left l = head' l : take' (left - 1) (tail' l)

drop' :: Int -> [a] -> [a]
drop' 0 l = l
drop' left [] = []
drop' left l = drop' (left - 1) (tail' l)

filter' :: (a -> Bool) -> [a] -> [a]
filter' f [] = [] 
filter' f l = if f (head' l)
              then head' l : filter' f (tail' l)
              else filter' f (tail' l)

foldl' :: (a -> b -> a) -> a -> [b] -> a
foldl' f z [] = z
foldl' f z l = foldl' f (f z (head' l)) (tail' l) 

concat' :: [a] -> [a] -> [a]
concat' [] l = l
concat' l1 l2 = head' l1 : concat' (tail' l1) l2

quickSort' :: Ord a => [a] -> [a]
quickSort' [] = []
quickSort' (x : []) = x : []
quickSort' (x : l) = concat' (quickSort' (filter' (\ h -> h <= x) l))  (x : (quickSort' (filter' (\ h -> h > x) l))) 
