# 1. Installatie
Om de applicatie te kunnen gebruiken moeten er enkele programma's geïnstalleerd worden.  
De installatie van deze programma's worden hieronder beschreven.

## 1.1 Anaconda
Om te beginnen gaat er Anaconda geïnstalleerd worden.  

Anaconda kan gedownload worden op de volgende [link](https://repo.anaconda.com/archive/).  
Kies hierbij voor de Anaconda versie `Anaconda3-2019.07` van jouw platform.  
Vervolgens kan dit geïnstalleerd worden hierbij wordt aangeraden om voor de optie `Register Anaconda as the system Python 3.7` te kiezen.

Wanneer dit is geïnstalleerd kan Anaconda ingesteld worden. Door Anaconda op deze manier in te stellen wordt het makkelijker om de packages van dit project te beheren.
- Open een nieuw Anaconda terminal
- Maak een nieuw Anaconda environment door het volgende commando uit te voeren, en vervang NAAM door een naam naar keuze, in dit voorbeeld BD02:  
  `conda create -n BD02 pip python=3.6`
- Vervolgens moet deze environment geactiveerd worden om hier verandering aan te kunnen brengen. Dit wordt gedaan door het volgende commando uit te voeren:
  `conda activate BD02`
- Dit zou ervoor moeten zorgen dat het volgende te zien is in de terminal: `(BD02) C:`. Hierdoor kan eenvoudig gezien worden in welk environment je momenteel werkt.

## 1.2 C++ Build Tools
Nadat Anaconda is geïnstalleerd kan er verder gegaan worden met het installeren van C++ Build Tools.  
Om dit te installeren moet Visual Studio gedownload worden, dit kan gevonden worden op de volgende [link](https://visualstudio.microsoft.com/vs/community/).

Als je Visual Studio al geïnstalleerd hebt kan je de installatie aanpassen en ervoor zorgen dat de nieuwe workload toegevoegd wordt.

Wanneer dit geïnstalleerd wordt moet er gekozen worden welke workloads gedownload worden. Kies hier de workload  
`Desktop development with C++`.  
Als deze workload gedownload is kan er doorgegaan worden naar de volgende stap.

## 1.3 Protoc
Na het installeren van Anaconda en C++ Build Tools kan de library genaamd Protoc geïnstalleerd worden.
Dit kan gedownload worden op deze [link](https://github.com/protocolbuffers/protobuf/releases).  
Vervolgens kan er genavigeerd worden naar de laatste release van Protocolbuffers. Download vervolgens het zip-bestand met de naam protoc gevolgd met de versie van Protoc van jouw platform. 
Dit kan bijvoorbeeld `protoc-3.15.6-win64.zip` zijn.

Wanneer dit gedownload is moet het ZIP-bestand uitgepakt worden. Vervolgens kan de uitgepakte map in een eigen gekozen map geplaatst worden.
Hierna moet er genavigeerd worden naar de `bin` map. Het pad van de `bin` map moet vervolgens gekopieerd worden, bijv: `H:/Programs/Protoc/bin`.
Dit pad moet vervolgens toegevoegd worden aan de PATH gegevens van je computer.

## 1.4 Tensorflow
Tenserflow wordt gebruikt voor het trainen/gebruiken van object detectie modellen.

Kloon de tensorflow repository via [link](https://github.com/tensorflow/models).
Open de command promt (cmd) als administrator. Voor de volgende stap wordt [git.bach](https://gitforwindows.org/) gebruikt.
Ga naar de `../models/research` en type hier het commando: `protoc object_detection/protos/*.proto --python_out=.` en kopieer de python setup file door middel van het commando:`cp object_detection/packages/tf2/setup.py .`.
Vervolg dit met de installatie door middel van het commando: `python -m pip install.`. 


## 1.5 CUDA en cuDNN (optioneel)
**Deze stap kan alleen uitgevoerd worden wanneer je een Nvidia GPU hebt.**

CUDA en cuDNN versnelt het training proces waardoor tijdens het trainen gebruik gemaakt kan worden van de grafische processor.
- Download [link](https://developer.nvidia.com/cuda-toolkit-archive) Cuda Toolkit Archive;
- Download [link](https://developer.nvidia.com/rdp/cudnn-archive) cuDNN Archive.

Selecteer `Cuda 11.0.3` en `cuDNN 8.0.5.39` voor de juiste versie. Ga na de NVIDIA [developer](https://developer.nvidia.com/) en maak hier een account aan of log in.
Wanneer er ingelogd is kan het downloaden vervolgd worden door op `continue donwload` de klikken. De gedownloade `zip` bestanden kunnen uitgepakt worden.
- Verplaats de file van in de `bin` folder van cuDNN naar de `bin` folder van Cuda. 
- Verplaats nu de file van in de `include` folder van cuDNN naar de `include` folder van Cuda.
- Verplaats nu de file van in de `lib\x64` folder van cuDNN naar de `lib\x64` folder van Cuda.

## 1.6 LabelImg (optioneel)
**Deze stap hoeft alleen uitgevoerd te worden als je afbeeldingen wilt gaan labelen voor het model.**

Aangezien LabelImg een externe repository is moet deze apart gekloond worden. De repository kan gekloond worden door middel van deze [link](https://github.com/tzutalin/labelImg).
Wanneer LabelImg gekloond is kan LabelImg gestart worden door `labelimg.py` te runnen. Tijdens het gebruik van LabelImg moet dan alleen nog de `save dir` en `open dir` geselecteerd te worden.


---
_Bij vragen neem contact op met casusgroep 11_