#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <algorithm>
#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <Xinput.h>
#include <atomic>
#include <string>
#include <vector>
#include <cstdio>
#include "ui_strings.h"
#include "imgui.h"
#include "backends/imgui_impl_win32.h"
#include "backends/imgui_impl_dx11.h"
extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND,UINT,WPARAM,LPARAM);

static ID3D11Device* device=nullptr;
static ID3D11DeviceContext* context=nullptr;
static HWND window=nullptr;
static WNDPROC previousProc=nullptr;
static bool initialized=false,f8Held=false;
static bool gamepadHeld=false;
static HMODULE inputModule=nullptr;
static DWORD (WINAPI *inputState)(DWORD,XINPUT_STATE*)=nullptr;
static std::atomic<bool> visible{false};
static std::atomic<int> command{0};
static int selected=0,mode=0;
static std::string status=T(u8"等待运行时连接");
static bool canApply=false;
static std::string reward;
static bool canClaim=false;
static HRESULT lastError=S_OK;
static constexpr UINT nativeEscapeDown=WM_APP+0x4BD,nativeEscapeUp=WM_APP+0x4BE;
static bool escapeHeld=false;
static ULONGLONG escapeReleaseAt=0;
struct Entry {int id;std::string name,description;int quality=0,elements=0;};
static std::vector<Entry> recipes,auras,plans;
static int planSelected=0;
static char planName[192]{};
static int auraSelected=0,auraSlot=0;
static char auraSearch[192]{};
static std::string auraSlots;
static int page=0,quality=0,element=0;
static bool pageChanged=false,padActive=false,scrollSelection=false,padArmed=false;
static DWORD lastPad=0,repeatDirection=0;
static ULONGLONG repeatAt=0;
static int activePad=-1;
static bool ownsFocus(){
#ifdef BD_UI_TEST
 return true; // 仅独立测试 DLL：不抢正在运行的游戏焦点。
#else
 return GetForegroundWindow()==window;
#endif
}
extern "C" __declspec(dllexport) void BDLanguage(int value){uiLanguage=value;auraSearch[0]=0;quality=element=0;}
extern "C" __declspec(dllexport) void BDCatalogClear(){recipes.clear();auras.clear();auraSelected=0;}
extern "C" __declspec(dllexport) void BDRecipe(int id,const char* name,const char* description){recipes.push_back({id,name,description});}
extern "C" __declspec(dllexport) void BDAura(int id,const char* name,const char* description,int tier,int tags){auras.push_back({id,name,description,tier,tags});}
extern "C" __declspec(dllexport) void BDAuraSlots(const char* text){auraSlots=text;}
static std::vector<int> filteredAuras(){std::vector<int> ids;for(int i=0;i<(int)auras.size();i++)if((!quality||auras[i].quality==quality)&&(!element||(auras[i].elements&(1<<(element-1))))&&auras[i].name.find(auraSearch)!=std::string::npos)ids.push_back(i);return ids;}
extern "C" __declspec(dllexport) void BDAuraPlansClear(){plans.clear();}
extern "C" __declspec(dllexport) void BDAuraPlan(int id,const char* name,const char* description){plans.push_back({id,name,description});planSelected=std::clamp(planSelected,0,(int)plans.size()-1);}
extern "C" __declspec(dllexport) const char* BDAuraPlanName(){return planName;}
static void normalizeAura(){auto ids=filteredAuras();if(!ids.empty()&&std::find(ids.begin(),ids.end(),auraSelected)==ids.end())auraSelected=ids[0];scrollSelection=true;}
static void moveSelection(int delta){
 if(page==0){if(!recipes.empty())selected=std::clamp(selected+delta,0,(int)recipes.size()-1);}
 else if(page==2){if(!plans.empty())planSelected=std::clamp(planSelected+delta,0,(int)plans.size()-1);}
 else{auto ids=filteredAuras();if(!ids.empty()){auto it=std::find(ids.begin(),ids.end(),auraSelected);int at=it==ids.end()?0:(int)(it-ids.begin());auraSelected=ids[std::clamp(at+delta,0,(int)ids.size()-1)];}}
 scrollSelection=true;
}
// 独立语义导航：不依赖 ImGui 后端只探测索引 0 的 XInput 导航。
static void handlePad(const XINPUT_GAMEPAD& input){
 DWORD buttons=input.wButtons;
 if(input.sThumbLY>16000)buttons|=XINPUT_GAMEPAD_DPAD_UP;
 if(input.sThumbLY<-16000)buttons|=XINPUT_GAMEPAD_DPAD_DOWN;
 if(input.sThumbLX>16000)buttons|=XINPUT_GAMEPAD_DPAD_RIGHT;
 if(input.sThumbLX<-16000)buttons|=XINPUT_GAMEPAD_DPAD_LEFT;
 if(input.bLeftTrigger>100)buttons|=0x10000;
 if(input.bRightTrigger>100)buttons|=0x20000;
 const bool chord=(buttons&0x30)==0x30;
 if(chord&&!gamepadHeld){visible=!visible;command.store(visible?0x1000:0x1001);padActive=true;padArmed=false;scrollSelection=true;}
 gamepadHeld=chord;
 if(!visible){lastPad=buttons;return;}
 if(!padArmed){if(buttons==0){padArmed=true;lastPad=0;}return;}
 DWORD edges=buttons&~lastPad;
 if(edges)padActive=true;
 if(edges&XINPUT_GAMEPAD_Y&&page!=1){command.store(0x600000+(uiLanguage?0:1));lastPad=buttons;return;}
 if(edges&XINPUT_GAMEPAD_B){visible=false;command.store(0x1001);padArmed=false;lastPad=buttons;return;}
 if(edges&(XINPUT_GAMEPAD_LEFT_SHOULDER|XINPUT_GAMEPAD_RIGHT_SHOULDER)){page=(page+(edges&XINPUT_GAMEPAD_RIGHT_SHOULDER?1:2))%3;pageChanged=true;scrollSelection=true;}
 DWORD direction=buttons&(0xf|0x30000);auto now=GetTickCount64();
 if(direction){bool step=direction!=repeatDirection||now>=repeatAt;if(step){
  repeatAt=now+(direction!=repeatDirection?350:110);
  if(direction&XINPUT_GAMEPAD_DPAD_UP)moveSelection(-1);
  else if(direction&XINPUT_GAMEPAD_DPAD_DOWN)moveSelection(1);
  else if(direction&0x10000)moveSelection(-8);
  else if(direction&0x20000)moveSelection(8);
  else if(direction&XINPUT_GAMEPAD_DPAD_LEFT){if(page==1)auraSlot=(auraSlot+4)%5;else if(page==0)mode=0;}
  else if(direction&XINPUT_GAMEPAD_DPAD_RIGHT){if(page==1)auraSlot=(auraSlot+1)%5;else if(page==0)mode=1;}
 }repeatDirection=direction;}else repeatDirection=0;
 if(page==1&&edges&XINPUT_GAMEPAD_RIGHT_THUMB){quality=(quality+1)%5;normalizeAura();}
 if(page==1&&edges&XINPUT_GAMEPAD_LEFT_THUMB){auraSearch[0]=0;quality=element=0;normalizeAura();}
 if(page==1&&edges&XINPUT_GAMEPAD_X){element=(element+1)%6;normalizeAura();}
 if(!page&&edges&XINPUT_GAMEPAD_X&&canClaim)command.store(0x3000);
 if(page==1&&edges&XINPUT_GAMEPAD_Y)command.store(0x400000+auraSlot*1024);
 if(page==2&&edges&XINPUT_GAMEPAD_X)command.store(0x500000);
 if(edges&XINPUT_GAMEPAD_A){if(page==2){if(canApply&&!plans.empty())command.store(0x510000+planSelected);}else if(page==1){if(!filteredAuras().empty())command.store(0x400000+auraSlot*1024+auras[auraSelected].id);}else if(canApply&&!recipes.empty())command.store(1+selected+256*mode);}
 lastPad=buttons;
}
extern "C" __declspec(dllexport) uintptr_t BDInputAddress(){return reinterpret_cast<uintptr_t>(&inputState);}
extern "C" __declspec(dllexport) const char* BDUIState(){static char out[384];std::snprintf(out,sizeof(out),"{\"page\":%d,\"recipe\":%d,\"aura\":%d,\"slot\":%d,\"quality\":%d,\"element\":%d,\"pad\":%d,\"count\":%d,\"plans\":%d,\"plan\":%d}",page,selected,auras.empty()?0:auras[auraSelected].id,auraSlot+1,quality,element,activePad,(int)filteredAuras().size(),(int)plans.size(),planSelected);return out;}

static LRESULT CALLBACK WindowProc(HWND hwnd,UINT message,WPARAM w,LPARAM l){
 if(message==nativeEscapeDown)return CallWindowProcW(previousProc,hwnd,WM_KEYDOWN,VK_ESCAPE,0x00010001);
 if(message==nativeEscapeUp){escapeHeld=false;return CallWindowProcW(previousProc,hwnd,WM_KEYUP,VK_ESCAPE,0xC0010001);}
 if(initialized&&visible){
  if(message==WM_CHAR||message==WM_KEYDOWN||message==WM_LBUTTONDOWN||message==WM_MOUSEWHEEL)padActive=false;
  if(message==WM_MOUSEMOVE){static LPARAM oldPosition=0;if(l!=oldPosition)padActive=false;oldPosition=l;}
  ImGui_ImplWin32_WndProcHandler(hwnd,message,w,l);
  if(message==WM_KEYUP||message==WM_SYSKEYUP||message==WM_LBUTTONUP||message==WM_RBUTTONUP||message==WM_MBUTTONUP)
   return CallWindowProcW(previousProc,hwnd,message,w,l);
  if((message>=WM_KEYFIRST&&message<=WM_KEYLAST)||
     (message>=WM_MOUSEFIRST&&message<=WM_MOUSELAST))return 1;
 }
 return CallWindowProcW(previousProc,hwnd,message,w,l);
}

extern "C" __declspec(dllexport) uintptr_t BDPresentAddress(){
 HWND dummy=CreateWindowExW(0,L"STATIC",L"Astral BD renderer probe",WS_POPUP,0,0,16,16,nullptr,nullptr,GetModuleHandleW(nullptr),nullptr);
 if(!dummy){lastError=HRESULT_FROM_WIN32(GetLastError());return 0;}
 DXGI_SWAP_CHAIN_DESC desc{};desc.BufferCount=1;desc.BufferDesc.Width=16;desc.BufferDesc.Height=16;
 desc.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;desc.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;
 desc.OutputWindow=dummy;desc.SampleDesc.Count=1;desc.Windowed=TRUE;desc.SwapEffect=DXGI_SWAP_EFFECT_DISCARD;
 IDXGISwapChain* chain=nullptr;ID3D11Device* dev=nullptr;ID3D11DeviceContext* ctx=nullptr;
 lastError=D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,
 D3D11_SDK_VERSION,&desc,&chain,&dev,nullptr,&ctx);
 uintptr_t result=0;
 if(SUCCEEDED(lastError))result=reinterpret_cast<uintptr_t>((*reinterpret_cast<void***>(chain))[8]);
 if(ctx)ctx->Release();if(dev)dev->Release();if(chain)chain->Release();DestroyWindow(dummy);return result;
}

extern "C" __declspec(dllexport) long BDError(){return lastError;}
extern "C" __declspec(dllexport) int BDCommand(){return command.exchange(0);}
extern "C" __declspec(dllexport) void BDStatus(const char* text,int allowed){status=text;canApply=allowed!=0;}
extern "C" __declspec(dllexport) void BDVisible(int value){visible=value!=0;}
extern "C" __declspec(dllexport) void BDSelection(int index,int selectedMode){selected=index;mode=selectedMode;}
extern "C" __declspec(dllexport) int BDIsVisible(){return visible?1:0;}
extern "C" __declspec(dllexport) uintptr_t BDWindow(){return reinterpret_cast<uintptr_t>(window);}
extern "C" __declspec(dllexport) int BDRendererState(){return (initialized?1:0)|(inputState?2:0);}
extern "C" __declspec(dllexport) int BDEscapePending(){return escapeHeld?1:0;}
extern "C" __declspec(dllexport) int BDNativeEscape(){
 if(!initialized||escapeHeld)return 0;
 escapeHeld=true;escapeReleaseAt=GetTickCount64()+120;
 PostMessageW(window,nativeEscapeDown,0,0);return 1;
}
extern "C" __declspec(dllexport) void BDReward(const char* text,int allowed){reward=text;canClaim=allowed!=0;}

extern "C" __declspec(dllexport) void BDRender(IDXGISwapChain* chain){
 DXGI_SWAP_CHAIN_DESC desc{};if(FAILED(chain->GetDesc(&desc)))return;
 if(!initialized){
  lastError=chain->GetDevice(__uuidof(ID3D11Device),reinterpret_cast<void**>(&device));
  if(FAILED(lastError))return;
  device->GetImmediateContext(&context);window=desc.OutputWindow;
  IMGUI_CHECKVERSION();ImGui::CreateContext();auto& io=ImGui::GetIO();io.IniFilename=nullptr;
  io.ConfigFlags|=ImGuiConfigFlags_NavEnableKeyboard;
  wchar_t windowsPath[MAX_PATH];GetWindowsDirectoryW(windowsPath,MAX_PATH);
  std::wstring fontPath=std::wstring(windowsPath)+L"\\Fonts\\msyh.ttc";
  if(GetFileAttributesW(fontPath.c_str())==INVALID_FILE_ATTRIBUTES)fontPath=std::wstring(windowsPath)+L"\\Fonts\\segoeui.ttf";
  int needed=WideCharToMultiByte(CP_UTF8,0,fontPath.c_str(),-1,nullptr,0,nullptr,nullptr);
  std::string utf8(needed,'\0');WideCharToMultiByte(CP_UTF8,0,fontPath.c_str(),-1,utf8.data(),needed,nullptr,nullptr);
  if(!io.Fonts->AddFontFromFileTTF(utf8.c_str(),24,nullptr,io.Fonts->GetGlyphRangesChineseFull())){
   lastError=E_FAIL;ImGui::DestroyContext();context->Release();device->Release();context=nullptr;device=nullptr;return;
  }
  ImGui::StyleColorsDark();auto& style=ImGui::GetStyle();style.WindowRounding=12;style.FrameRounding=6;
  style.WindowPadding=ImVec2(24,22);style.ItemSpacing=ImVec2(12,12);
  if(!ImGui_ImplWin32_Init(window)||!ImGui_ImplDX11_Init(device,context)){lastError=E_FAIL;return;}
  previousProc=reinterpret_cast<WNDPROC>(SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(WindowProc)));
  initialized=true;
  inputModule=LoadLibraryW(L"xinput1_4.dll");
  if(inputModule)inputState=reinterpret_cast<decltype(inputState)>(GetProcAddress(inputModule,"XInputGetState"));
 }
 if(escapeHeld&&escapeReleaseAt&&GetTickCount64()>=escapeReleaseAt){escapeReleaseAt=0;PostMessageW(window,nativeEscapeUp,0,0);}
 if(ownsFocus()){
  bool down=(GetAsyncKeyState(VK_F8)&0x8000)!=0;
  if(down&&!f8Held){visible=!visible;command.store(visible?0x1000:0x1001);}f8Held=down;
  XINPUT_STATE chosen{};int found=-1;
  if(inputState)for(DWORD index=0;index<4;index++){XINPUT_STATE input{};if(inputState(index,&input)!=ERROR_SUCCESS)continue;if(found<0){chosen=input;found=(int)index;}if(input.Gamepad.wButtons||input.Gamepad.bLeftTrigger>100||input.Gamepad.bRightTrigger>100||std::abs((int)input.Gamepad.sThumbLX)>16000||std::abs((int)input.Gamepad.sThumbLY)>16000){chosen=input;found=(int)index;break;}if((int)index==activePad){chosen=input;found=(int)index;}}
  if(found>=0){activePad=found;handlePad(chosen.Gamepad);}else{activePad=-1;lastPad=0;repeatDirection=0;gamepadHeld=false;padArmed=false;}
 }else{lastPad=0;repeatDirection=0;padArmed=false;}
 if(!visible)return;
 ImGui_ImplDX11_NewFrame();ImGui_ImplWin32_NewFrame();ImGui::NewFrame();
 auto& io=ImGui::GetIO();io.MouseDrawCursor=!padActive;
 ImVec2 size(std::min(1000.0f,io.DisplaySize.x-48),std::min(880.0f,io.DisplaySize.y-48));
 ImGui::SetNextWindowPos(ImVec2((io.DisplaySize.x-size.x)/2,(io.DisplaySize.y-size.y)/2),ImGuiCond_Always);
 ImGui::SetNextWindowSize(size,ImGuiCond_Always);
 ImGui::Begin(T(u8"星界战士 · BD 选择"),nullptr,ImGuiWindowFlags_NoCollapse|ImGuiWindowFlags_NoResize|ImGuiWindowFlags_NoMove);
 ImGui::TextWrapped("%s",padActive?T(u8"LB/RB 切页 · 上下/左摇杆选择 · LT/RT 快速翻页 · B 收起"):T(u8"F8 或 Back＋Start 打开或关闭。进入本轮后可立即装配。版本：2.6.4"));
 int requestedLanguage=uiLanguage;
 ImGui::SetNextItemWidth(140);
 if(ImGui::Combo("Language / 语言",&requestedLanguage,"简体中文\0English\0"))command.store(0x600000+requestedLanguage);
 ImGui::SameLine();ImGui::TextUnformatted(uiLanguage?"Y on Builds/Plans: language":"BD/方案页 Y：切换语言");
 const char* qualities[]={T(u8"全部品质"),T(u8"普通 / I"),T(u8"稀有 / II"),T(u8"史诗 / III"),T(u8"星界")};
 const char* elements[]={T(u8"全部元素"),T(u8"火"),T(u8"冰"),T(u8"雷"),T(u8"毒"),T(u8"通用")};
 ImGui::Separator();
 const int requestedPage=page;
 if(ImGui::BeginTabBar("pages")){
 if(ImGui::BeginTabItem(T(u8"BD 构筑"),nullptr,pageChanged&&requestedPage==0?ImGuiTabItemFlags_SetSelected:0)){
 if(!pageChanged||requestedPage==0)page=0;
 ImGui::BeginChild("recipes",ImVec2(0,170),true);
 for(int i=0;i<(int)recipes.size();i++){
  ImGui::PushID(i);if(ImGui::Selectable(recipes[i].name.c_str(),selected==i,0,ImVec2(0,30)))selected=i;ImGui::PopID();
  if(scrollSelection&&selected==i)ImGui::SetScrollHereY();
 }
 ImGui::EndChild();
 if(padActive)ImGui::TextWrapped(T(u8"左右切换模式 · A 立即装配 · X 领取成长补给"));
 if(!recipes.empty())ImGui::TextWrapped("%s",recipes[selected].description.c_str());
 ImGui::RadioButton(T(u8"成型模式"),&mode,0);ImGui::SameLine();ImGui::RadioButton(T(u8"成长模式"),&mode,1);
 ImGui::TextWrapped("%s",mode==0?T(u8"立即替换五个光环、四个法术及首槽符文，并保存本轮装备。"):T(u8"立即装配法术，随后四次补给逐步发放五个光环与符文。"));
 ImGui::Separator();ImGui::TextWrapped("%s",status.c_str());
 if(!reward.empty()){
  ImGui::TextWrapped("%s",reward.c_str());
  ImGui::BeginDisabled(!canClaim);
  if(ImGui::Button(T(u8"领取成长补给"),ImVec2(190,42)))command.store(0x3000);
  ImGui::EndDisabled();
 }
 ImGui::BeginDisabled(!canApply);
 if(ImGui::Button(T(u8"立即装配此 BD"),ImVec2(220,42)))command.store(1+selected+256*mode);
 ImGui::EndDisabled();ImGui::EndTabItem();
 }
 if(ImGui::BeginTabItem(T(u8"光环自选"),nullptr,pageChanged&&requestedPage==1?ImGuiTabItemFlags_SetSelected:0)){
 if(!pageChanged||requestedPage==1)page=1;
 ImGui::TextWrapped(T(u8"仅修改所选光环槽，立即生效并保存；支持重复光环。"));
 ImGui::SetNextItemWidth(200);ImGui::InputText(T(u8"方案名（可选）"),planName,sizeof(planName));
 ImGui::SameLine();if(ImGui::Button(T(u8"保存当前五槽")))command.store(0x500000);
 ImGui::SameLine();if(ImGui::Button(T(u8"已保存方案"))){page=2;pageChanged=true;}
 ImGui::SetNextItemWidth(180);if(ImGui::Combo(T(u8"等级 / 品质"),&quality,qualities,5))normalizeAura();
 ImGui::SameLine();ImGui::SetNextItemWidth(170);if(ImGui::Combo(T(u8"元素"),&element,elements,6))normalizeAura();
 ImGui::SetNextItemWidth(240);if(ImGui::InputText(T(u8"搜索名称（可选）"),auraSearch,sizeof(auraSearch)))normalizeAura();
 ImGui::SameLine();if(ImGui::Button(T(u8"重置筛选"))){auraSearch[0]=0;quality=element=0;normalizeAura();}
 if(padActive)ImGui::TextWrapped(T(u8"右摇杆：等级 · X：元素 · 左右：槽位 · A：装备 · Y：清空槽 · 左摇杆按下：重置筛选"));
 auto filtered=filteredAuras();ImGui::Text(T(u8"当前分类：%d 项"),(int)filtered.size());
 ImGui::BeginChild("auras",ImVec2(0,std::max(80.0f,std::min(100.0f,size.y-770.0f))),true);
 for(int i:filtered){
  ImGui::PushID(i);if(ImGui::Selectable(auras[i].name.c_str(),auraSelected==i))auraSelected=i;ImGui::PopID();
  if(scrollSelection&&auraSelected==i)ImGui::SetScrollHereY();
 }
 if(filtered.empty())ImGui::TextWrapped(T(u8"没有匹配光环，请切换分类或重置筛选。"));
 ImGui::EndChild();
 ImGui::BeginChild("auraDetails",ImVec2(0,100),true);
 if(!filtered.empty())ImGui::TextWrapped("%s · %s",auras[auraSelected].name.c_str(),auras[auraSelected].description.c_str());
 ImGui::EndChild();
 const char* slots[]={T(u8"光环槽 1"),T(u8"光环槽 2"),T(u8"光环槽 3"),T(u8"光环槽 4"),T(u8"光环槽 5")};
 ImGui::SetNextItemWidth(190);ImGui::Combo(T(u8"目标槽位"),&auraSlot,slots,5);
 ImGui::TextWrapped("%s",auraSlots.c_str());
 ImGui::TextWrapped("%s",status.c_str());
 ImGui::BeginDisabled(filtered.empty());if(ImGui::Button(T(u8"立即装备 / 替换"),ImVec2(230,42)))command.store(0x400000+auraSlot*1024+auras[auraSelected].id);ImGui::EndDisabled();
 ImGui::SameLine();if(ImGui::Button(T(u8"清空此槽"),ImVec2(150,42)))command.store(0x400000+auraSlot*1024);
 ImGui::EndTabItem();
 }
 if(ImGui::BeginTabItem(T(u8"光环方案"),nullptr,pageChanged&&requestedPage==2?ImGuiTabItemFlags_SetSelected:0)){
 if(!pageChanged||requestedPage==2)page=2;
 ImGui::TextWrapped(T(u8"保存当前五个光环槽；应用时一次替换五槽，包含空槽。法术保持当前配置。"));
 ImGui::SetNextItemWidth(220);ImGui::InputText(T(u8"方案名（留空自动命名）"),planName,sizeof(planName));
 if(ImGui::Button(T(u8"保存当前五槽为新方案"),ImVec2(250,42)))command.store(0x500000);
 if(padActive)ImGui::TextWrapped(T(u8"上下选择方案 · LT/RT 快速翻页 · A 立即应用 · X 保存当前五槽"));
 ImGui::Text(T(u8"已保存：%d 个方案"),(int)plans.size());
 ImGui::BeginChild("savedPlans",ImVec2(0,std::max(100.0f,std::min(200.0f,size.y-580.0f))),true);
 for(int i=0;i<(int)plans.size();i++){
  ImGui::PushID(i);if(ImGui::Selectable(plans[i].name.c_str(),planSelected==i))planSelected=i;ImGui::PopID();
  if(scrollSelection&&planSelected==i)ImGui::SetScrollHereY();
 }
 if(plans.empty())ImGui::TextWrapped(T(u8"还没有保存方案。先配置光环，再点击保存当前五槽。"));
 ImGui::EndChild();
 if(!plans.empty())ImGui::TextWrapped("%s",plans[planSelected].description.c_str());
 ImGui::TextWrapped("%s",status.c_str());
 ImGui::BeginDisabled(!canApply||plans.empty());
 if(ImGui::Button(T(u8"立即应用此光环方案"),ImVec2(260,42)))command.store(0x510000+planSelected);
 ImGui::EndDisabled();ImGui::EndTabItem();
 }
 ImGui::EndTabBar();
 }
 pageChanged=page!=requestedPage;scrollSelection=false;
 ImGui::Separator();
 if(ImGui::Button(T(u8"关闭 Mod"),ImVec2(160,42)))command.store(0x2000);
 ImGui::SameLine();if(ImGui::Button(T(u8"收起界面"),ImVec2(150,42))){visible=false;command.store(0x1001);}
 ImGui::End();ImGui::Render();
 ID3D11Texture2D* back=nullptr;ID3D11RenderTargetView* target=nullptr;
 if(FAILED(chain->GetBuffer(0,__uuidof(ID3D11Texture2D),reinterpret_cast<void**>(&back))))return;
 lastError=device->CreateRenderTargetView(back,nullptr,&target);back->Release();if(FAILED(lastError))return;
 ID3D11RenderTargetView* oldTarget=nullptr;ID3D11DepthStencilView* oldDepth=nullptr;
 context->OMGetRenderTargets(1,&oldTarget,&oldDepth);context->OMSetRenderTargets(1,&target,nullptr);
 ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());context->OMSetRenderTargets(1,&oldTarget,oldDepth);
 if(oldTarget)oldTarget->Release();if(oldDepth)oldDepth->Release();target->Release();
}

extern "C" __declspec(dllexport) void BDShutdown(){
 visible=false;if(!initialized)return;
 if(escapeHeld){CallWindowProcW(previousProc,window,WM_KEYUP,VK_ESCAPE,0xC0010001);escapeHeld=false;escapeReleaseAt=0;}
 SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(previousProc));
 ImGui_ImplDX11_Shutdown();ImGui_ImplWin32_Shutdown();ImGui::DestroyContext();
 context->Release();device->Release();device=nullptr;context=nullptr;initialized=false;
 if(inputModule)FreeLibrary(inputModule);inputModule=nullptr;inputState=nullptr;gamepadHeld=false;f8Held=false;
 recipes.clear();auras.clear();plans.clear();planSelected=0;planName[0]=0;
 page=quality=element=0;pageChanged=padActive=scrollSelection=padArmed=false;lastPad=repeatDirection=0;repeatAt=0;activePad=-1;
}
