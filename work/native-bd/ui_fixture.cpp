#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
LRESULT CALLBACK Proc(HWND h,UINT m,WPARAM w,LPARAM l){if(m==WM_DESTROY){PostQuitMessage(0);return 0;}return DefWindowProcW(h,m,w,l);}
int WINAPI wWinMain(HINSTANCE instance,HINSTANCE,LPWSTR,int){
 WNDCLASSW cls{};cls.lpfnWndProc=Proc;cls.hInstance=instance;cls.lpszClassName=L"AstralBDUITest";RegisterClassW(&cls);
 HWND window=CreateWindowW(cls.lpszClassName,L"BD 手柄界面测试",WS_OVERLAPPEDWINDOW,40,40,1280,1080,nullptr,nullptr,instance,nullptr);
 DXGI_SWAP_CHAIN_DESC desc{};desc.BufferCount=1;desc.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;desc.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;desc.OutputWindow=window;desc.SampleDesc.Count=1;desc.Windowed=TRUE;desc.SwapEffect=DXGI_SWAP_EFFECT_DISCARD;
 IDXGISwapChain* chain=nullptr;ID3D11Device* dev=nullptr;ID3D11DeviceContext* ctx=nullptr;
 if(FAILED(D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&desc,&chain,&dev,nullptr,&ctx)))return 1;
 ShowWindow(window,SW_SHOWNOACTIVATE);MSG msg{};
 while(true){if(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){if(msg.message==WM_QUIT)break;TranslateMessage(&msg);DispatchMessageW(&msg);}else{chain->Present(0,0);Sleep(5);}}
 ctx->Release();dev->Release();chain->Release();return 0;
}
