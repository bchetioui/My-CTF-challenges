module SimpleParserLibrary where

import Data.Char (isAlpha, isAlphaNum, isDigit, isSpace)

data Parser b a = P (b -> [(a, b)])

parse :: Parser b a -> b -> [(a, b)]
parse (P p) inp = p inp

runParser p inp = case parse p inp of
                    [] -> error "parsing failed"
                    [(a, _)] -> a

instance Functor (Parser b) where  
  fmap f p = P $ \inp -> case parse p inp of
                           [] -> []
                           [(v, inp')] -> [(f v, inp')]

instance Applicative (Parser b) where  
  pure v = P $ \inp -> [(v, inp)]
  p <*> q = P $ \inp ->
    case parse p inp of
      [] -> []
      [(f, inp')] -> case parse q inp' of
                       [] -> []
                       [(v, inp'')] -> [(f v, inp'')]

instance Monad (Parser b) where
  p >>= f = P $ \inp -> case parse p inp of
                          [] -> []
                          [(v, inp')] -> parse (f v) inp'

(<|>) :: Parser b a -> Parser b a -> Parser b a
p <|> q = P $ \inp -> case parse p inp of
                        [] -> parse q inp
                        r -> r
failure :: Parser b a
failure = P $ \inp -> []

many :: Parser b a -> Parser b [a]
many1 :: Parser b a -> Parser b [a]
many1 p =
  p >>= \v ->
  many p >>= \vs ->
  return (v:vs)

many p = many1 p <|> return []

getState :: Parser b b
setState :: b -> Parser b ()
getState = P $ \st -> [(st, st)]
setState st = P $ \_ -> [((), st)]

lookahead :: Parser b a -> Parser b a
lookahead p =
  getState >>= \st ->
  p >>= \v ->
  setState st >>
  return v

notFollowedBy :: Parser b a -> Parser b ()
notFollowedBy p =
  getState >>= \st ->
  case parse (lookahead p) st of
    [] -> setState st
    [(v, st')] -> failure


--------------------
-- String parsers --
--------------------

type StringParser a = Parser String a

item :: StringParser Char
item = P $ \inp -> case inp of
                     (v:ss) -> [(v, ss)]
                     [] -> []

sat :: (Char -> Bool) -> StringParser Char
sat p = item >>= \v -> if (p v) then return v else failure
 
digit :: StringParser Char
digit = sat isDigit

char :: Char -> StringParser Char
char x = sat (== x)

token :: StringParser a -> StringParser a
token p = p <* many (sat isSpace)

top :: StringParser a -> StringParser a
top p = p <* (notFollowedBy item) -- must parse all of input
  
identifier :: StringParser String
identifier = token ((:) <$> sat isAlpha <*> many (sat isAlphaNum))

parens p = token (char '(') >> p <* token (char ')')

intLiteral :: StringParser Int
intLiteral = read <$> token (many1 digit <* notFollowedBy (sat isAlphaNum))
