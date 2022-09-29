# what-to-do-with-git
Dag Allen,

Hieronder lezen jullie een voorstel van hoe studenten met Git zouden kunnen werken. Dit voorbeeld kan tevens functioneren als template voor een Git-reposotory

## Repository Structuur
De repository structuur ziet er als volgt uit:
```
repository
|   README.md
|   .gitignore
|   .gitattributes
|---docs
|   |   index.html
|   |   <overige pagina's>.html
|
|---<project>
|   |   <project files>
|
|---lfs
    |   <project lfs files>
```

| File/Folder          | Beschrijving                                                                               |
|----------------------|--------------------------------------------------------------------------------------------|
| README.md            | Casus beschrijving, link naar GitHub Pages met documentatie, installatie instructies, etc. |
| .gitignore           | Files die niet worden meegenomen in het versie beheer, zo nodig gegenereerd                |
| .gitattributes       | Files die opgeslagen worden door middel van Git LFS                                        |
| (Folder) docs        | GitHub Pages met de complete documentatie, homepage is extended abstract                   |
| (Folder) \<project\> | Project met daarin code en/of andere deliverables                                          |
| (Folder) lfs         | Binary files, zoals afbeeldingen of PDF's, die wel in de repository moeten staan           |

## Hoe werk ik met Git

### [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
Geeft een overzicht van alle git-commando's

### [A Successful Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
Geeft een robuust model om hoe je met vertakkingen omgaat binnen git, hoe je als projectteam je workflow inricht en wat de functie van de master, development en andere vertakkingen zijn.

### [Generate a gitignore file](https://www.gitignore.io/)
Wordt gebruikt om je project clean te houden en alle local settings die je niet in de gezamenlijke repo wil hebben zitten. Met deze website genereer je automatisch deze file voor je taal of library naar keuze.

### [Mastering Markdown](https://guides.github.com/features/mastering-markdown)
Markdown is een eenvoudige markup taal die kan worden gebruikt om documenten op te maken.

#### [Markdown Table Generator](https://www.tablesgenerator.com/markdown_tables)
Het maken van tabellen in Markdown kan soms wat lastig zijn. Gelukkig zijn er handige tools beschikbaar die deze taak makkelijker maken.

### [Understanding the GitHub Flow](https://guides.github.com/introduction/flow/)
GitHub gebruikt een bepaalde workflow om met meerdere mensen tegelijk te kunnen werken aan een project.

### [GitHub for Education](https://education.github.com/)
Het is mogelijk voor studenten om gratis een GitHub Pro account aan te vragen (door je Zuyd email adres te linken met je GitHub account). Hierdoor wordt het mogelijk om meer collaborators toe te voegen aan een prive repository.

### [Git Large File System](https://git-lfs.github.com/)
Git kan niet goed om gaan met files die niet bestaan uit plaintext, zoals PNG's, JPG's of PDF's. Om dit probleem te verhelpen kan Git Large File System worden gebruikt.
