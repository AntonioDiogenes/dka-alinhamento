# DKA Alinhamento - Sistema Desktop

Sistema Desktop de Alinhamento e Geometria Veicular para Oficinas Mecânicas e Frotas Pesadas, desenvolvido em Python e Tkinter com arquitetura modular e persistência de dados.

---

## 🚀 Funcionalidades Principais

- **Gestão de Clientes e Frotas**: Cadastro completo com histórico de medições.
- **Configuração de Caminhões e Carretas**: Modelos de 2 a 12 eixos com personalização de tração, eixos direcionais e tolerâncias.
- **Painel de Sensores em Tempo Real**: Conexão Serial / Bluetooth para leitura de sensores (Dianteiro, Traseiro, Central).
- **Relatórios PDF Profissionais**: Geração de laudos técnicos detalhados com ReportLab.
- **Multiplataforma**: Compatível com Windows, Linux e macOS.

---

## 🛠️ Requisitos e Instalação

### Pré-requisitos
- Python 3.10 ou superior
- Pip

### Instalação das Dependências

```bash
pip install -r requirements.txt
```

### Executar em Desenvolvimento

```bash
python -m app.main
```

### Executar Testes Unitários

```bash
python -m unittest discover tests
```

---

## 📦 Compilação de Executáveis (Build Local)

### 🐧 Linux
Execute o script de automação:
```bash
./build_linux.sh
```
O binário será gerado em `dist/DKA_Alinhamento`.

### 🪟 Windows
Execute o script de automação (ou via Wine no Linux):
```bash
./build_windows_exe.sh
```
Ou no prompt do Windows:
```cmd
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm DKA_Alinhamento.spec
```
O executável será gerado em `dist/DKA_Alinhamento.exe`.

### 🍎 macOS
Execute o script de automação:
```bash
./build_macos.sh
```
O bundle `.app` será gerado em `dist/DKA_Alinhamento.app` e compactado em `dist/DKA_Alinhamento_macOS.zip`.

---

## 🤖 Integração Contínua (CI/CD - GitHub Actions)

O repositório está configurado com um fluxo automatizado em `.github/workflows/build.yml` que compila e gera executáveis em paralelo sempre que houver um `push` ou `pull request` na branch principal (`main` / `master`):

| Plataforma | Runner GitHub | Artefato Gerado |
|---|---|---|
| **Windows** | `windows-latest` | `DKA_Alinhamento.exe` |
| **Linux** | `ubuntu-latest` | `DKA_Alinhamento` / `DKA_Alinhamento-Linux-x64.tar.gz` |
| **macOS** | `macos-latest` | `DKA_Alinhamento.app` / `DKA_Alinhamento-macOS.zip` |

### Releases Automáticas
Ao criar e enviar uma tag de versão (ex: `git tag v1.0.0 && git push origin v1.0.0`), o GitHub Actions compila todas as versões e anexa os executáveis diretamente na aba **Releases** do repositório.
