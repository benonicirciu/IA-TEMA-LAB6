# Tema A - Evitare cu recuperare

### Descriere
Implementare mașină de stări finite pentru robotul Pioneer P3-DX.
Robotul trece prin următoarele stări:
1. **FORWARD**: Merge drept până vede un obstacol (< 0.5m).
2. **BACKWARD**: Dă înapoi 1s pentru a crea spațiu.
3. **TURNING**: Se rotește aleatoriu 1.5s pentru a schimba direcția.

### Parametri
- Viteză: 2.0 rad/s
- Distanță stop: 0.5 m

### Comenzi
- python -m venv .venv
- .venv\Scripts\activate
- pip install coppeliasim-zmqremoteapi-client
- python tema_a_rec.py
