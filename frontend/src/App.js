import React, { useState, useRef, useEffect, useCallback } from 'react';

const STYLES = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --cream:#faf7f2;--warm-white:#fffef9;
  --bark:#3d2b1f;--bark-mid:#5c4033;--bark-light:#7a5c4a;
  --amber:#c8722a;--amber-l:#e8944a;
  --sage:#5a7a5a;
  --parchment:#f0e8d8;--parchment-d:#ddd0b8;
  --panel:#16110e;--panel-l:#201810;
  --mono:#f0c060;
  --cyan:#4ab8c8;--cyan-d:#2a8898;
  --violet:#9878d8;--violet-d:#6040b0;
  --green:#5ab87a;--red:#d86858;
  --r:16px;--rs:8px;
}
html,body,#root{height:100%;font-family:'DM Sans',sans-serif;background:var(--cream);color:var(--bark);overflow:hidden}
.app{display:flex;height:100vh}

.lp{width:290px;flex-shrink:0;background:var(--panel);display:flex;flex-direction:column;border-right:1px solid rgba(255,255,255,.05)}
.lp-head{padding:18px 16px 12px;border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:10px}
.logo-icon{font-size:22px}
.logo-name{font-family:'Playfair Display',serif;font-size:19px;color:var(--cream)}
.logo-sub{font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--mono);opacity:.6;margin-top:1px}
.lp-body{flex:1;overflow-y:auto;padding:12px 0}
.lp-body::-webkit-scrollbar{width:3px}
.lp-body::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08)}
.sec{padding:0 14px 14px}
.sec-lbl{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.22);font-weight:600;padding:0 2px 8px}

.lg-topology{background:var(--panel-l);border:1px solid rgba(255,255,255,.07);border-radius:var(--rs);overflow:hidden}
.lg-node{display:flex;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid rgba(255,255,255,.04);transition:all .25s;border-left:2px solid transparent}
.lg-node:last-child{border-bottom:none}
.lg-node.active{background:rgba(152,120,216,.12);border-left-color:var(--violet)}
.lg-node.done{background:rgba(90,184,122,.07);border-left-color:var(--green)}
.lg-node-dot{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.15);flex-shrink:0;transition:all .3s}
.lg-node.active .lg-node-dot{background:var(--violet);box-shadow:0 0 6px var(--violet);animation:glow .9s infinite}
.lg-node.done .lg-node-dot{background:var(--green)}
.lg-node-name{font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,.4);transition:color .3s;flex:1}
.lg-node.active .lg-node-name{color:var(--violet);font-weight:500}
.lg-node.done .lg-node-name{color:var(--green)}
.lg-node-badge{font-size:9px;color:rgba(255,255,255,.18);background:rgba(255,255,255,.04);border-radius:3px;padding:1px 5px;font-family:'JetBrains Mono',monospace}
.lg-edge{display:flex;align-items:center;gap:5px;padding:3px 12px;opacity:.35}
.lg-edge-line{flex:1;height:1px;background:rgba(255,255,255,.1)}
.lg-edge-txt{font-size:9px;color:rgba(255,255,255,.25);font-family:'JetBrains Mono',monospace;white-space:nowrap}
@keyframes glow{0%,100%{opacity:1}50%{opacity:.4}}

.mcp-cards{display:flex;flex-direction:column;gap:5px}
.mc{background:var(--panel-l);border:1px solid rgba(255,255,255,.06);border-radius:var(--rs);padding:9px 11px;transition:all .25s;border-left:2px solid transparent}
.mc.done{border-left-color:var(--green);background:rgba(90,184,122,.05)}
.mc-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:3px}
.mc-name{font-size:11px;font-weight:600;color:rgba(255,255,255,.45);transition:color .25s}
.mc.done .mc-name{color:var(--green)}
.mc-port{font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,255,255,.2)}
.mc-tools{display:flex;flex-wrap:wrap;gap:2px}
.mc-t{font-size:9px;font-family:'JetBrains Mono',monospace;color:rgba(255,255,255,.2);background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);border-radius:2px;padding:1px 4px}

.ctx-block{background:var(--panel-l);border:1px solid rgba(255,255,255,.06);border-radius:var(--rs);padding:10px 12px}
.ctx-r{display:flex;justify-content:space-between;align-items:center;padding:2px 0;border-bottom:1px solid rgba(255,255,255,.03)}
.ctx-r:last-child{border-bottom:none}
.ctx-k{font-size:10px;color:rgba(255,255,255,.28);text-transform:capitalize}
.ctx-v{font-size:10px;font-weight:500;color:var(--mono);font-family:'JetBrains Mono',monospace;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ctx-empty{font-size:11px;color:rgba(255,255,255,.15);text-align:center;padding:5px 0;font-style:italic}

.qp{width:100%;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:6px;padding:6px 10px;font-size:11px;color:rgba(255,255,255,.35);cursor:pointer;text-align:left;transition:all .2s;font-family:'DM Sans',sans-serif;line-height:1.4;margin-bottom:4px;display:block}
.qp:hover{background:rgba(74,184,200,.1);border-color:rgba(74,184,200,.3);color:var(--cyan)}
.qp:last-child{margin-bottom:0}

.chat{flex:1;display:flex;flex-direction:column;background:var(--warm-white);overflow:hidden;min-width:0}
.chat-head{padding:14px 20px;border-bottom:1px solid var(--parchment);display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.ch-t{font-family:'Playfair Display',serif;font-size:16px;color:var(--bark)}
.ch-s{font-size:11px;color:var(--bark-light);opacity:.5;margin-top:2px}
.badges{display:flex;gap:5px}
.badge{display:flex;align-items:center;gap:4px;border-radius:20px;padding:3px 10px;font-size:10px;font-weight:500}
.badge.lg{background:rgba(152,120,216,.1);border:1px solid rgba(152,120,216,.3);color:var(--violet-d)}
.badge.mcp{background:rgba(74,184,200,.1);border:1px solid rgba(74,184,200,.3);color:var(--cyan-d)}
.b-dot{width:5px;height:5px;border-radius:50%;animation:glow 2s infinite}
.badge.lg .b-dot{background:var(--violet)}
.badge.mcp .b-dot{background:var(--cyan)}

.msgs{flex:1;overflow-y:auto;padding:16px 20px;display:flex;flex-direction:column;gap:14px}
.msgs::-webkit-scrollbar{width:3px}
.msgs::-webkit-scrollbar-thumb{background:var(--parchment-d);border-radius:2px}

.mg{display:flex;flex-direction:column;gap:2px}
.mg.user{align-items:flex-end}
.mg.assistant{align-items:flex-start}
.av{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;margin-bottom:2px;font-weight:700}
.mg.assistant .av{background:#8B6F47;color:white;box-shadow:0 2px 6px rgba(0,0,0,0.3);border:1px solid #6B5437}
.mg.user .av{background:var(--amber);color:white;font-weight:600;font-size:11px}
.bub{max-width:66%;padding:11px 15px;border-radius:var(--r);line-height:1.65;font-size:13px}
.mg.assistant .bub{background:var(--parchment);border:1px solid var(--parchment-d);border-bottom-left-radius:4px;color:var(--bark)}
.mg.user .bub{background:var(--amber);color:white;border-bottom-right-radius:4px}
.bub p{margin-bottom:5px}.bub p:last-child{margin-bottom:0}
.bub ul,.bub ol{padding-left:16px;margin:4px 0}.bub li{margin-bottom:2px}

.tool-tags{display:flex;flex-wrap:wrap;gap:3px;margin-top:7px}
.tt{display:inline-flex;align-items:center;gap:2px;border-radius:3px;padding:2px 6px;font-size:9.5px;font-family:'JetBrains Mono',monospace}
.tt.lgt{background:rgba(152,120,216,.1);border:1px solid rgba(152,120,216,.2);color:var(--violet-d)}
.tt.mcpt{background:rgba(74,184,200,.1);border:1px solid rgba(74,184,200,.2);color:var(--cyan-d)}

.typing{display:flex;align-items:center;gap:3px;padding:11px 15px;background:var(--parchment);border:1px solid var(--parchment-d);border-radius:var(--r);border-bottom-left-radius:4px;width:fit-content}
.td{width:5px;height:5px;background:var(--bark-light);border-radius:50%;opacity:.3;animation:tp 1.4s infinite ease-in-out}
.td:nth-child(2){animation-delay:.2s}.td:nth-child(3){animation-delay:.4s}
@keyframes tp{0%,80%,100%{opacity:.3;transform:scale(1)}40%{opacity:1;transform:scale(1.15)}}

.ni{display:flex;align-items:center;gap:6px;background:var(--panel);border:1px solid rgba(152,120,216,.3);border-radius:var(--rs);padding:7px 11px;max-width:280px;font-size:11px;font-family:'JetBrains Mono',monospace}
.ni-spin{width:11px;height:11px;border:2px solid rgba(152,120,216,.2);border-top-color:var(--violet);border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}
.ni-node{color:var(--violet)}
.ni-arr{color:rgba(255,255,255,.2);font-size:10px}
.ni-tool{color:var(--mono)}

.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;text-align:center;padding:24px}
.w-icon{font-size:50px}
.w-title{font-family:'Playfair Display',serif;font-size:24px;color:var(--bark)}
.w-sub{font-size:13px;color:var(--bark-light);opacity:.6;max-width:360px;line-height:1.6}
.w-chips{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;max-width:460px}
.wc{background:var(--parchment);border:1px solid var(--parchment-d);border-radius:20px;padding:6px 13px;font-size:12px;cursor:pointer;transition:all .2s;color:var(--bark);font-family:'DM Sans',sans-serif}
.wc:hover{background:var(--amber);color:white;border-color:var(--amber);transform:translateY(-1px)}

.ia{padding:11px 20px 15px;border-top:1px solid var(--parchment);flex-shrink:0;background:var(--warm-white)}
.iw{display:flex;align-items:flex-end;gap:7px;background:var(--parchment);border:1.5px solid var(--parchment-d);border-radius:13px;padding:6px 6px 6px 13px;transition:all .2s}
.iw:focus-within{border-color:var(--amber);box-shadow:0 0 0 3px rgba(200,114,42,.1)}
#ci{flex:1;border:none;background:transparent;font-family:'DM Sans',sans-serif;font-size:13px;color:var(--bark);resize:none;outline:none;line-height:1.5;max-height:100px;min-height:22px;padding:3px 0}
#ci::placeholder{color:rgba(61,43,31,.3)}
.sb{width:34px;height:34px;border-radius:9px;background:var(--amber);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .2s;color:white}
.sb:hover:not(:disabled){background:var(--bark);transform:scale(1.05)}
.sb:disabled{opacity:.33;cursor:not-allowed}
.hint{font-size:10px;color:rgba(61,43,31,.25);text-align:center;margin-top:5px}

.rp{width:280px;flex-shrink:0;background:var(--panel);display:flex;flex-direction:column;border-left:1px solid rgba(255,255,255,.05)}
.rp-head{padding:14px 14px 10px;border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;justify-content:space-between}
.rp-title{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.28)}
.rp-cnt{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--mono);background:rgba(240,192,96,.1);border:1px solid rgba(240,192,96,.2);border-radius:3px;padding:1px 6px}
.rp-body{flex:1;overflow-y:auto;padding:8px}
.rp-body::-webkit-scrollbar{width:3px}
.rp-body::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08)}
.tc{background:var(--panel-l);border:1px solid rgba(255,255,255,.06);border-radius:var(--rs);margin-bottom:6px;overflow:hidden;cursor:pointer;transition:border-color .2s}
.tc:hover{border-color:rgba(255,255,255,.12)}
.tc.open{border-color:rgba(240,192,96,.2)}
.tc-head{display:flex;align-items:center;gap:5px;padding:7px 9px}
.tc-num{font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,255,255,.18);width:14px}
.tc-name{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:var(--mono);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tc-srv{font-size:8.5px;color:var(--cyan);background:rgba(74,184,200,.08);border:1px solid rgba(74,184,200,.15);border-radius:3px;padding:1px 4px;white-space:nowrap}
.tc-ms{font-size:9px;font-family:'JetBrains Mono',monospace;color:rgba(255,255,255,.18)}
.tc-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.tc-dot.ok{background:var(--green)}.tc-dot.err{background:var(--red)}
.tc-body{padding:0 9px 8px;display:none}
.tc.open .tc-body{display:block}
.tc-lbl{font-size:8.5px;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.18);margin:5px 0 3px}
.tc-pre{font-family:'JetBrains Mono',monospace;font-size:9.5px;color:rgba(255,255,255,.5);background:rgba(0,0,0,.22);border-radius:4px;padding:5px 7px;overflow:auto;white-space:pre;max-height:100px;line-height:1.5}
.tc-pre::-webkit-scrollbar{width:2px;height:2px}
.tc-pre::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12)}
.rp-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:8px;opacity:.25}
.rp-ei{font-size:26px}.rp-et{font-size:11px;color:rgba(255,255,255,.4);text-align:center;line-height:1.5}

@media(max-width:1100px){.rp{display:none}}
@media(max-width:720px){.lp{display:none}.bub{max-width:85%}}
`;

const LANGGRAPH_NODES = [
  {id:'START',     label:'START',     badge:'entry'},
  {id:'agent',     label:'agent',     badge:'LLM node'},
  {id:'tool_node', label:'tool_node', badge:'ToolNode'},
  {id:'END',       label:'END',       badge:'terminal'},
];
const LG_EDGES = [
  {label:'always'},
  {label:'tool_calls?'},
  {label:'loop back'},
];

const MCP_SERVERS = [
  {id:'availability',name:'Availability',  port:3101,icon:'📅',tools:['check_availability','list_groomers']},
  {id:'pricing',     name:'Pricing Engine',port:3102,icon:'💰',tools:['get_pricing','list_addons']},
  {id:'booking',     name:'Booking',       port:3103,icon:'✅',tools:['create_booking','get_booking','cancel_booking']},
  {id:'notification',name:'Notifications', port:3104,icon:'📬',tools:['send_notification','get_notifications']},
];
const TOOL_TO_SERVER={};
MCP_SERVERS.forEach(s=>s.tools.forEach(t=>{TOOL_TO_SERVER[t]=s.id;}));
const CTX_LABELS={petType:'Pet Type',petSize:'Pet Size',petName:'Pet Name',service:'Service',lastBookingId:'Booking ID'};
const QUICK_PROMPTS=['Book a full groom for my golden retriever tomorrow evening','Check evening slots for a cat this weekend','How much for a large dog full groom with nail trim?','What add-ons do you offer?'];
const WELCOME_CHIPS=['🐕 Book dog grooming','🐈 Groom my cat','📅 Check availability','💰 View pricing','📋 List add-ons'];

function renderMd(text){
  if(!text) return <p style={{color:'#999'}}>No response</p>;
  const lines=text.split('\n');const out=[];let i=0;
  while(i<lines.length){
    const l=lines[i];
    if(!l.trim()){i++;continue;}
    if(l.match(/^[\-\*•]\s+/)||l.match(/^\d+\.\s+/)){
      const items=[];
      while(i<lines.length&&(lines[i].match(/^[\-\*•]\s+/)||lines[i].match(/^\d+\.\s+/))){items.push(lines[i].replace(/^[\-\*•]\s+/,'').replace(/^\d+\.\s+/,''));i++;}
      const T=lines[i-1]?.match(/^\d+\./)?'ol':'ul';
      out.push(<T key={i} style={{paddingLeft:16,margin:'4px 0'}}>{items.map((x,j)=><li key={j} dangerouslySetInnerHTML={{__html:fi(x)}} style={{marginBottom:2}}/>)}</T>);
      continue;
    }
    out.push(<p key={i} dangerouslySetInnerHTML={{__html:fi(l)}} style={{marginBottom:4}}/>);i++;
  }
  return out;
}
function fi(t){
  return t
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,'<em>$1</em>')
    .replace(/`(.+?)`/g,'<code style="background:rgba(0,0,0,.07);padding:1px 5px;border-radius:3px;font-family:monospace;font-size:.9em">$1</code>')
    .replace(/\$(\d+)/g,'<strong style="color:#5a7a5a">$$$1</strong>');
}

export default function App(){
  const [messages,    setMessages]    = useState([]);
  const [input,       setInput]       = useState('');
  const [loading,     setLoading]     = useState(false);
  const [apiMessages, setApiMessages] = useState([]);
  const [sessionCtx,  setSessionCtx]  = useState({});
  const [toolCallLog, setToolCallLog] = useState([]);
  const [activeNode,  setActiveNode]  = useState(null);
  const [doneNodes,   setDoneNodes]   = useState(new Set());
  const [doneServers, setDoneServers] = useState(new Set());
  const [expandedTC,  setExpandedTC]  = useState(null);
  const msgsRef=useRef(null);const inputRef=useRef(null);

  useEffect(()=>{msgsRef.current?.scrollTo({top:msgsRef.current.scrollHeight,behavior:'smooth'});},[messages,loading]);

  const send=useCallback(async(text)=>{
    const content=text||input.trim();
    if(!content||loading) return;
    setInput('');
    if(inputRef.current) inputRef.current.style.height='auto';
    setActiveNode('agent');setDoneNodes(new Set());setDoneServers(new Set());

    const userMsg={id:Date.now(),role:'user',content,ts:new Date()};
    setMessages(p=>[...p,userMsg]);
    const newApi=[...apiMessages,{role:'user',content}];
    setApiMessages(newApi);
    setLoading(true);

    try{
      const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:newApi,sessionContext:sessionCtx})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error||'Server error');

      const log=data.toolCallLog||[];
      setToolCallLog(p=>[...p,...log]);
      const usedSrvs=new Set(log.map(e=>e.server));
      const usedNodes=new Set(['agent']);
      if(log.length>0) usedNodes.add('tool_node');
      setDoneNodes(usedNodes);setDoneServers(usedSrvs);setActiveNode(null);

      if(data.contextUpdates) setSessionCtx(p=>({...p,...data.contextUpdates}));
      const lc=content.toLowerCase();
      if(lc.includes('dog')) setSessionCtx(p=>({...p,petType:'dog'}));
      if(lc.includes('cat')) setSessionCtx(p=>({...p,petType:'cat'}));
      if(lc.includes('rabbit')) setSessionCtx(p=>({...p,petType:'rabbit'}));

      const msgContent=data.message||data.response||JSON.stringify(data);
      const am={id:Date.now()+1,role:'assistant',content:msgContent,toolsUsed:data.toolsUsed||[],toolCallLog:log,graphMeta:data.graphMeta,ts:new Date()};
      setMessages(p=>[...p,am]);
      setApiMessages(p=>[...p,{role:'assistant',content:msgContent}]);
    }catch(err){
      setMessages(p=>[...p,{id:Date.now()+1,role:'assistant',content:`⚠️ Error: ${err.message}\n\nMake sure:\n- All MCP servers running (\`npm start\`)\n- Agent on port 3100\n- GEMINI_API_KEY is set`,ts:new Date()}]);
      setActiveNode(null);
    }finally{setLoading(false);}
  },[input,loading,apiMessages,sessionCtx]);

  const ns=(nid)=>{if(activeNode===nid) return 'active';if(doneNodes.has(nid)) return 'done';return '';};
  const ss=(sid)=>doneServers.has(sid)?'done':'';

  return(
    <>
      <style>{STYLES}</style>
      <div className="app">
        <aside className="lp">
          <div className="lp-head">
            <span className="logo-icon">🐾</span>
            <div><div className="logo-name">PawBook</div><div className="logo-sub">LangGraph + MCP</div></div>
          </div>
          <div className="lp-body">
            <div className="sec">
              <div className="sec-lbl">LangGraph Graph</div>
              <div className="lg-topology">
                {LANGGRAPH_NODES.map((n,idx)=>(
                  <React.Fragment key={n.id}>
                    <div className={`lg-node ${ns(n.id)}`}>
                      <div className="lg-node-dot"/>
                      <span className="lg-node-name">{n.label}</span>
                      <span className="lg-node-badge">{n.badge}</span>
                    </div>
                    {idx<LANGGRAPH_NODES.length-1&&(
                      <div className="lg-edge">
                        <div className="lg-edge-line"/>
                        <span className="lg-edge-txt">{LG_EDGES[idx]?.label}</span>
                        <div className="lg-edge-line"/>
                      </div>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
            <div className="sec">
              <div className="sec-lbl">MCP Servers (via LangChain)</div>
              <div className="mcp-cards">
                {MCP_SERVERS.map(s=>(
                  <div key={s.id} className={`mc ${ss(s.id)}`}>
                    <div className="mc-top"><span className="mc-name">{s.icon} {s.name}</span><span className="mc-port">:{s.port}</span></div>
                    <div className="mc-tools">{s.tools.map(t=><span key={t} className="mc-t">{t}</span>)}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="sec">
              <div className="sec-lbl">Session Context</div>
              <div className="ctx-block">
                {Object.keys(sessionCtx).length===0
                  ?<div className="ctx-empty">No context yet</div>
                  :Object.entries(sessionCtx).filter(([k])=>CTX_LABELS[k]).map(([k,v])=>(
                    <div className="ctx-r" key={k}><span className="ctx-k">{CTX_LABELS[k]}</span><span className="ctx-v">{String(v)}</span></div>
                  ))
                }
              </div>
            </div>
            <div className="sec">
              <div className="sec-lbl">Quick Prompts</div>
              {QUICK_PROMPTS.map((p,i)=><button key={i} className="qp" onClick={()=>send(p)}>{p}</button>)}
            </div>
          </div>
        </aside>

        <main className="chat">
          <div className="chat-head">
            <div>
              <div className="ch-t">PawBook Reservations</div>
              <div className="ch-s">LangGraph state machine · LangChain DynamicStructuredTool · MCP JSON-RPC · Gemini free</div>
            </div>
            <div className="badges">
              <div className="badge lg"><div className="b-dot"/>LangGraph</div>
              <div className="badge mcp"><div className="b-dot"/>MCP</div>
            </div>
          </div>
          <div className="msgs" ref={msgsRef}>
            {messages.length===0?(
              <div className="welcome">
                <div className="w-icon">🐾</div>
                <div className="w-title">Welcome to PawBook</div>
                <div className="w-sub">LangGraph orchestrates Gemini through LangChain tools, each backed by a real MCP server.</div>
                <div className="w-chips">{WELCOME_CHIPS.map((c,i)=><button key={i} className="wc" onClick={()=>send(c.replace(/^[^\s]+\s/,''))}>{c}</button>)}</div>
              </div>
            ):(
              messages.map(msg=>(
                <div key={msg.id} className={`mg ${msg.role}`}>
                  <div className="av">{msg.role==='assistant'?'🐕':'U'}</div>
                  <div className="bub">
                    {renderMd(msg.content)}
                    {msg.toolsUsed?.length>0&&(
                      <div className="tool-tags" style={{marginTop:7}}>
                        <span className="tt lgt">⬡ LangGraph</span>
                        {msg.toolsUsed.map((t,i)=>{
                          const srv=MCP_SERVERS.find(s=>s.id===TOOL_TO_SERVER[t]);
                          return <span key={i} className="tt mcpt" title={srv?`MCP :${srv.port}`:''}>{srv?.icon} {t}</span>;
                        })}
                      </div>
                    )}
                    {msg.graphMeta&&(
                      <div style={{fontSize:10,color:'rgba(61,43,31,.3)',marginTop:5,fontFamily:'JetBrains Mono,monospace'}}>
                        {msg.graphMeta.toolCallCount} MCP calls · {msg.graphMeta.totalMessages} msgs in graph state
                      </div>
                    )}
                  </div>
                  <div style={{fontSize:10,color:'rgba(61,43,31,.25)',marginTop:2,padding:'0 4px'}}>
                    {msg.ts?.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}
                  </div>
                </div>
              ))
            )}
            {loading&&(
              <div className="mg assistant">
                <div className="av">🐕</div>
                {activeNode?(
                  <div className="ni">
                    <div className="ni-spin"/>
                    <span className="ni-node">{activeNode}</span>
                    <span className="ni-arr">→</span>
                    <span className="ni-tool">MCP tools</span>
                  </div>
                ):(
                  <div className="typing"><div className="td"/><div className="td"/><div className="td"/></div>
                )}
              </div>
            )}
          </div>
          <div className="ia">
            <div className="iw">
              <textarea id="ci" ref={inputRef}
                placeholder="Ask about availability, pricing, or book an appointment..."
                value={input} onChange={e=>setInput(e.target.value)}
                onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}}
                onInput={e=>{e.target.style.height='auto';e.target.style.height=Math.min(e.target.scrollHeight,100)+'px';}}
                rows={1} disabled={loading}
              />
              <button className="sb" onClick={()=>send()} disabled={!input.trim()||loading}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </button>
            </div>
            <div className="hint">Enter to send · Shift+Enter for new line</div>
          </div>
        </main>

        <aside className="rp">
          <div className="rp-head">
            <span className="rp-title">MCP Inspector</span>
            {toolCallLog.length>0&&<span className="rp-cnt">{toolCallLog.length}</span>}
          </div>
          <div className="rp-body">
            {toolCallLog.length===0?(
              <div className="rp-empty"><div className="rp-ei">🔬</div><div className="rp-et">LangGraph tool calls via MCP appear here</div></div>
            ):(
              [...toolCallLog].reverse().map((tc,i)=>{
                const idx=toolCallLog.length-i;const isOpen=expandedTC===idx;
                return(
                  <div key={idx} className={`tc ${isOpen?'open':''}`} onClick={()=>setExpandedTC(isOpen?null:idx)}>
                    <div className="tc-head">
                      <span className="tc-num">#{idx}</span>
                      <span className="tc-name">{tc.tool}</span>
                      <span className="tc-srv">{tc.server}</span>
                      <span className="tc-ms">{tc.elapsed}</span>
                      <div className={`tc-dot ${tc.result?.success!==false?'ok':'err'}`}/>
                    </div>
                    <div className="tc-body">
                      <div className="tc-lbl">LangChain → MCP → {tc.serverUrl}</div>
                      <pre className="tc-pre">{JSON.stringify(tc.args,null,2)}</pre>
                      <div className="tc-lbl">MCP Response</div>
                      <pre className="tc-pre">{JSON.stringify({...tc.result,_meta:undefined},null,2)}</pre>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
