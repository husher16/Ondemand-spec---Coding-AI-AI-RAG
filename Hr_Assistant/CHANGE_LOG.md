## 03

- Sync Documenti

## 04

- tasti db info e db reindex

## 05

- Semantic Chunking

## 06

- Refactoring Semantic Chunking

## 07

- lettura di file di tipo diverso 
- libreria utilizzata: https://github.com/microsoft/markitdown

```
$ poetry add markitdown
```

in semantic chunking aggiunta funzione _split_into_sentences per evitare che un file riporti una singola frase.


## 08 - Upload file da interfaccia

- possibilita' di aggiungere uno o piu' file in resumes da interfaccia, e all'aggiunta, lanciare l'aggiornamento del database degli embeddings
- nuova action per azzerare il database