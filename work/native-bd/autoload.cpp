#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>

static HMODULE self;
static INIT_ONCE versionOnce=INIT_ONCE_STATIC_INIT;
static HMODULE realVersion;
static BOOL CALLBACK loadVersion(PINIT_ONCE,void*,void**){
 wchar_t path[MAX_PATH];UINT n=GetSystemDirectoryW(path,MAX_PATH);
 if(!n||n>=MAX_PATH-13)return FALSE;
 std::wstring full(path,n);full+=L"\\version.dll";
 realVersion=LoadLibraryExW(full.c_str(),nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);
 return realVersion!=nullptr;
}
template<class T>static T original(const char* name){
 if(!InitOnceExecuteOnce(&versionOnce,loadVersion,nullptr,nullptr))return nullptr;
 return reinterpret_cast<T>(GetProcAddress(realVersion,name));
}
extern "C" FARPROC resolveVersion(unsigned index){
 static const char* names[]={"GetFileVersionInfoA","GetFileVersionInfoByHandle","GetFileVersionInfoExA","GetFileVersionInfoExW","GetFileVersionInfoSizeA","GetFileVersionInfoSizeExA","GetFileVersionInfoSizeExW","GetFileVersionInfoSizeW","GetFileVersionInfoW","VerFindFileA","VerFindFileW","VerInstallFileA","VerInstallFileW","VerLanguageNameA","VerLanguageNameW","VerQueryValueA","VerQueryValueW"};
 FARPROC p=original<FARPROC>(names[index]);if(!p)RaiseFailFastException(nullptr,nullptr,0);return p;
}
extern "C" BOOL WINAPI bdGetFileVersionInfoA(LPCSTR name,DWORD handle,DWORD size,LPVOID data){
 auto f=original<BOOL(WINAPI*)(LPCSTR,DWORD,DWORD,LPVOID)>("GetFileVersionInfoA");return f?f(name,handle,size,data):FALSE;
}
extern "C" DWORD WINAPI bdGetFileVersionInfoSizeA(LPCSTR name,LPDWORD handle){
 auto f=original<DWORD(WINAPI*)(LPCSTR,LPDWORD)>("GetFileVersionInfoSizeA");return f?f(name,handle):0;
}
extern "C" BOOL WINAPI bdVerQueryValueA(LPCVOID block,LPCSTR key,LPVOID* value,PUINT size){
 auto f=original<BOOL(WINAPI*)(LPCVOID,LPCSTR,LPVOID*,PUINT)>("VerQueryValueA");return f?f(block,key,value,size):FALSE;
}
struct WindowProbe { DWORD pid; bool found; };
static BOOL CALLBACK probe(HWND h,LPARAM context){
 auto* p=reinterpret_cast<WindowProbe*>(context);DWORD owner=0;RECT r{};
 GetWindowThreadProcessId(h,&owner);
 if(owner==p->pid&&IsWindowVisible(h)&&GetClientRect(h,&r)&&r.right*r.bottom>300000){p->found=true;return FALSE;}
 return TRUE;
}
static DWORD WINAPI start(void*){
 // 等到真正的游戏窗口存在，Steam 短命的启动进程不启动控制器。
 WindowProbe p{GetCurrentProcessId(),false};
 for(int i=0;i<300&&!p.found;i++){EnumWindows(probe,reinterpret_cast<LPARAM>(&p));if(!p.found)Sleep(200);}
 if(!p.found)return 0;
 wchar_t path[32768];DWORD n=GetModuleFileNameW(self,path,32768);if(!n||n>=32768)return 0;
 std::wstring root(path,n);root.resize(root.find_last_of(L"\\/"));root+=L"\\astral_bd";
 std::wstring python=root+L"\\runtime\\python.exe";
 std::wstring command=L"\""+python+L"\" \""+root+L"\\autoload.py\"";
 STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};
 if(CreateProcessW(python.c_str(),command.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,root.c_str(),&si,&pi)){CloseHandle(pi.hThread);CloseHandle(pi.hProcess);}
 else MessageBoxW(nullptr,L"BD Mod failed to start bundled Python. Reinstall the complete package.\nBD Mod 自动加载失败：无法启动随包 Python。请重新安装 Mod。",L"Astral Ascent BD Mod / 星界战士 BD Mod",MB_OK|MB_ICONERROR);
 return 0;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID){
 if(reason==DLL_PROCESS_ATTACH){self=module;DisableThreadLibraryCalls(module);HANDLE t=CreateThread(nullptr,0,start,nullptr,0,nullptr);if(t)CloseHandle(t);}
 return TRUE;
}
