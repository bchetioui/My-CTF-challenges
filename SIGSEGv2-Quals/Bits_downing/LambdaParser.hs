module LambdaParser (
  module LambdaParser,
  runParser
  )
where

import LambdaSyntax
import SimpleParserLibrary 

lambda = top application
  
application :: StringParser E
application = do
  ls <- many1 notapplication
  return $ foldl1 App ls

notapplication :: StringParser E
notapplication = variable <|>
                 abstraction <|>
                 parens application

variable :: StringParser E
variable = identifier >>= \v -> return $ Var v

abstraction :: StringParser E
abstraction = do
  token (char '\\')
  v <- identifier
  token (char '.')
  e <- application
  return $ Abs v e
