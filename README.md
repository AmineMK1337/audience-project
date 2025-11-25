##workflow
<img src="assets/image.png" width="400">

## Project Structure
```bash
/audience-project
├── /backend              
│   ├── /app
│   │   ├── /agents                 
│   │   │   ├── __init__.py
│   │   │   ├── base.py             
│   │   │   ├── pacing.py          
│   │   │   ├── grouper.py          
│   │   │   └── sentiment.py        
│   │   ├── /core
│   │   │   └── config.py           # env variables
│   │   ├── /routers                
│   │   │   ├── websocket.py      
│   │   │   └── reactions.py        
│   │   ├── /schemas                
│   │   │   ├── reactions.py        
│   │   │   └── feedback.py         # Text Questions
│   │   ├── /services               
│   │   │   ├── firestore.py        # Google Firestore CRUD operations
│   │   │   └── gemini_client.py    # gemini api wrapper
│   │   └── main.py                 
│   ├── Dockerfile                  # for cloud run
│   └── requirements.txt
│
├── /frontend               
│   ├── /src
│   │   ├── /app                    
│   │   │   ├── /audience           
│   │   │   │   └── page.tsx
│   │   │   ├── /presenter          
│   │   │   │   └── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx            
│   │   ├── /components             
│   │   │   ├── /dashboard
│   │   │   │   ├── LiveHeatmap.tsx 
│   │   │   │   ├── AgentAlert.tsx   
│   │   │   │   └── QuestionFeed.tsx
│   │   │   └── /interaction
│   │   │       ├── ReactionBtn.tsx 
│   │   │       └── TextInput.tsx
│   │   ├── /hooks
│   │   │   └── useSocket.ts        # Custom hook for WebSocket management
│   │   ├── /lib
│   │   │   └── types.ts            
│   │   └── /styles
│   │       └── globals.css         
│   ├── Dockerfile                  # For Cloud Run deployment
│   ├── next.config.js
│   └── tailwind.config.ts
├── .gitignore
└── README.md                       
