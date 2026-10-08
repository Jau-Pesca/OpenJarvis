#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#import <ImageIO/ImageIO.h>
#import <unistd.h>
#import <sys/stat.h>
static NSString *responseFile=nil;
static void emit(NSDictionary *data) { NSData *value=[NSJSONSerialization dataWithJSONObject:data options:0 error:nil]; if(responseFile) { NSError *error=nil; if(![value writeToFile:responseFile options:NSDataWritingAtomic error:&error]) { fprintf(stderr,"Não foi possível gravar resposta nativa.\n"); exit(2); } } else puts([[NSString alloc] initWithData:value encoding:NSUTF8StringEncoding].UTF8String); }
static void fail(NSString *message) { emit(@{@"ok":@NO,@"error":message}); exit(1); }
static id attr(AXUIElementRef element, NSString *key) { CFTypeRef result=NULL; if(AXUIElementCopyAttributeValue(element,(__bridge CFStringRef)key,&result)!=kAXErrorSuccess) return nil; return CFBridgingRelease(result); }
static CGRect frame(AXUIElementRef element) {
    CGPoint p=CGPointZero; CGSize s=CGSizeZero;
    id pos=attr(element,@"AXPosition"),size=attr(element,@"AXSize");
    if(pos && CFGetTypeID((__bridge CFTypeRef)pos)==AXValueGetTypeID()) AXValueGetValue((__bridge AXValueRef)pos,kAXValueCGPointType,&p);
    if(size && CFGetTypeID((__bridge CFTypeRef)size)==AXValueGetTypeID()) AXValueGetValue((__bridge AXValueRef)size,kAXValueCGSizeType,&s);
    return CGRectMake(p.x,p.y,s.width,s.height);
}
static void walk(AXUIElementRef element,int depth,NSMutableArray *nodes,int *count) {
    if(depth>12 || *count>=500 || nodes.count>=100) return; (*count)++;
    NSString *role=attr(element,@"AXRole") ?: @""; if([role isEqual:@"AXSecureTextField"]) return;
    NSMutableArray *text=[NSMutableArray array];
    for(NSString *key in @[@"AXTitle",@"AXDescription",@"AXValue"]) { id value=attr(element,key); if([value isKindOfClass:NSString.class] && [value length] && ![text containsObject:value]) [text addObject:[value substringToIndex:MIN([value length],240)]]; }
    CGRect f=frame(element);
    if(text.count && f.size.width>0 && f.size.height>0) [nodes addObject:@{@"role":role,@"text":[text componentsJoinedByString:@" | "],@"x":@(CGRectGetMidX(f)),@"y":@(CGRectGetMidY(f))}];
    NSArray *children=attr(element,@"AXChildren"); if([children isKindOfClass:NSArray.class]) for(id child in children) walk((__bridge AXUIElementRef)child,depth+1,nodes,count);
}
static NSDictionary *bounds(CGRect f) { return @{@"x":@(f.origin.x),@"y":@(f.origin.y),@"width":@(f.size.width),@"height":@(f.size.height)}; }
static NSDictionary *cursorPosition(void) { CGEventRef event=CGEventCreate(NULL); if(!event) return @{}; CGPoint p=CGEventGetLocation(event); CFRelease(event); return @{@"x":@(p.x),@"y":@(p.y)}; }
static NSData *scaledJPEG(NSString *path, size_t width, size_t height) {
    CGImageSourceRef source=CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path],NULL);
    if(!source) return nil;
    CGImageRef image=CGImageSourceCreateImageAtIndex(source,0,NULL); CFRelease(source);
    if(!image) return nil;
    NSBitmapImageRep *bitmap=[[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:width pixelsHigh:height bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
    CGColorSpaceRef colors=CGColorSpaceCreateDeviceRGB();
    CGContextRef context=bitmap?CGBitmapContextCreate(bitmap.bitmapData,width,height,8,bitmap.bytesPerRow,colors,kCGImageAlphaPremultipliedLast|kCGBitmapByteOrder32Big):NULL;
    CGColorSpaceRelease(colors);
    if(!context) { CGImageRelease(image); return nil; }
    CGContextSetInterpolationQuality(context,kCGInterpolationHigh);
    CGContextDrawImage(context,CGRectMake(0,0,width,height),image);
    CGContextRelease(context); CGImageRelease(image);
    return [bitmap representationUsingType:NSBitmapImageFileTypeJPEG properties:@{NSImageCompressionFactor:@.7}];
}
static CGEventRef keyboardEvent(CGKeyCode code, bool down, CGEventFlags flags) {
    static CGEventSourceRef source=NULL;
    if(!source) source=CGEventSourceCreate(kCGEventSourceStatePrivate);
    if(!source) fail(@"Não foi possível criar a fonte de eventos do teclado");
    CGEventRef event=CGEventCreateKeyboardEvent(source,code,down);
    if(!event) fail(@"Não foi possível criar o evento de teclado");
    CGEventSetFlags(event,flags); return event;
}
static void postKeyboard(CGKeyCode code, bool down, CGEventFlags flags) { CGEventRef event=keyboardEvent(code,down,flags); CGEventPost(kCGHIDEventTap,event); CFRelease(event); }
static void keyEvent(CGKeyCode code, CGEventFlags flags) {
    if(flags & kCGEventFlagMaskCommand) { postKeyboard(55,true,kCGEventFlagMaskCommand); [NSThread sleepForTimeInterval:.02]; }
    postKeyboard(code,true,flags); [NSThread sleepForTimeInterval:.02]; postKeyboard(code,false,flags);
    if(flags & kCGEventFlagMaskCommand) postKeyboard(55,false,0);
    [NSThread sleepForTimeInterval:.3];
}
static void typeEvent(NSString *text) {
    UniChar *chars=calloc(MAX(text.length,1),sizeof(UniChar));
    if(!chars) fail(@"Não foi possível preparar o texto");
    [text getCharacters:chars range:NSMakeRange(0,text.length)];
    for(NSUInteger index=0;index<text.length;) {
        NSUInteger length=1;
        if(chars[index]>=0xD800 && chars[index]<=0xDBFF && index+1<text.length && chars[index+1]>=0xDC00 && chars[index+1]<=0xDFFF) length=2;
        for(int i=0;i<2;i++) { CGEventRef e=keyboardEvent(0,!i,0); CGEventKeyboardSetUnicodeString(e,length,chars+index); CGEventPost(kCGHIDEventTap,e); CFRelease(e); }
        index+=length; [NSThread sleepForTimeInterval:.002];
    }
    free(chars); [NSThread sleepForTimeInterval:.3];
}
static void movePoint(CGPoint p) {
    CGEventRef initial=CGEventCreate(NULL); CGPoint start=CGEventGetLocation(initial); CFRelease(initial);
    for(int i=1;i<=24;i++) { double t=(double)i/24, eased=t*t*(3-2*t); CGPoint point=CGPointMake(start.x+(p.x-start.x)*eased,start.y+(p.y-start.y)*eased); CGWarpMouseCursorPosition(point); CGEventRef e=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,point,kCGMouseButtonLeft); CGEventPost(kCGHIDEventTap,e); CFRelease(e); [NSThread sleepForTimeInterval:.025]; }
}
static void clickPoint(CGPoint p) { movePoint(p); [NSThread sleepForTimeInterval:.15]; for(int i=0;i<2;i++) { CGEventRef e=CGEventCreateMouseEvent(NULL,i?kCGEventLeftMouseUp:kCGEventLeftMouseDown,p,kCGMouseButtonLeft); CGEventPost(kCGHIDEventTap,e); CFRelease(e); [NSThread sleepForTimeInterval:.08]; } }
static BOOL clickChrome(AXUIElementRef e, int depth) {
    if(depth>8) return NO;
    NSString *role=attr(e,@"AXRole"), *title=attr(e,@"AXTitle");
    if([role isEqual:@"AXDockItem"] && [title isEqual:@"Google Chrome"]) { CGRect f=frame(e); if(f.size.width>0 && f.size.height>0) { clickPoint(CGPointMake(CGRectGetMidX(f),CGRectGetMidY(f))); return YES; } }
    NSArray *children=attr(e,@"AXChildren"); if([children isKindOfClass:NSArray.class]) for(id child in children) if(clickChrome((__bridge AXUIElementRef)child,depth+1)) return YES;
    return NO;
}
int main(int argc, const char *argv[]) { @autoreleasepool {
    NSData *input=nil;
    if(argc>1) {
        if(argc!=5 || strcmp(argv[1],"--request-file") || strcmp(argv[3],"--response-file")) fail(@"Argumentos inválidos");
        NSString *request=[NSString stringWithUTF8String:argv[2]], *response=[NSString stringWithUTF8String:argv[4]];
        NSString *parent=request.stringByDeletingLastPathComponent; struct stat directory, file, existing;
        if(!request.isAbsolutePath || !response.isAbsolutePath || ![parent isEqual:response.stringByDeletingLastPathComponent] || [request isEqual:response] || lstat(parent.fileSystemRepresentation,&directory) || !S_ISDIR(directory.st_mode) || directory.st_uid!=getuid() || (directory.st_mode & 077) || lstat(request.fileSystemRepresentation,&file) || !S_ISREG(file.st_mode) || file.st_uid!=getuid()) fail(@"Arquivos de comunicação devem ficar em diretório privado do usuário");
        if(lstat(response.fileSystemRepresentation,&existing)==0 && (!S_ISREG(existing.st_mode) || existing.st_uid!=getuid())) fail(@"Arquivo de resposta inválido");
        responseFile=response;
        input=[NSData dataWithContentsOfFile:request];
        if(!input.length) fail(@"Pedido vazio");
    } else input=[[NSFileHandle fileHandleWithStandardInput] readDataToEndOfFile];
    if(input.length==0) {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
        [NSApp activateIgnoringOtherApps:YES];
        AXIsProcessTrustedWithOptions((__bridge CFDictionaryRef)@{(__bridge NSString *)kAXTrustedCheckOptionPrompt:@YES});
        CGRequestScreenCaptureAccess();
        NSAlert *alert=[[NSAlert alloc] init]; alert.messageText=@"Controle do Mac para OpenJarvis";
        alert.informativeText=@"Em Privacidade e Segurança > Acessibilidade, adicione e habilite JarvisMacControl. Se o macOS pedir Automação do Google Chrome, permita também. Habilite também Gravação de Tela para JarvisMacControl. Pedidos explícitos na conversa autorizam o uso do computador para executar a tarefa. Depois reabra OpenJarvis Interface.command.";
        [alert addButtonWithTitle:@"Abrir ajustes"]; [alert addButtonWithTitle:@"Fechar"];
        if([alert runModal]==NSAlertFirstButtonReturn) [NSWorkspace.sharedWorkspace openURL:[NSURL URLWithString:@"x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"]];
        return 0;
    }
    NSDictionary *r=[NSJSONSerialization JSONObjectWithData:input options:0 error:nil];
    if(![r isKindOfClass:NSDictionary.class]) fail(@"Pedido inválido");
    NSString *action=r[@"action"];
    NSArray *bundles=@[@"com.google.Chrome",@"com.apple.iWork.Numbers",@"com.microsoft.Excel",@"com.apple.finder"];
    if([action isEqual:@"status"]) { NSMutableArray *apps=[NSMutableArray array]; for(NSRunningApplication *a in NSWorkspace.sharedWorkspace.runningApplications) if(a.bundleIdentifier && [bundles containsObject:a.bundleIdentifier]) [apps addObject:@{@"bundle":a.bundleIdentifier,@"pid":@(a.processIdentifier),@"name":a.localizedName?:a.bundleIdentifier}]; emit(@{@"ok":@YES,@"accessibility":@(AXIsProcessTrusted()),@"screen_recording":@(CGPreflightScreenCaptureAccess()),@"posting_events":@(CGPreflightPostEventAccess()),@"apps":apps,@"pid":@(getpid()),@"parent_pid":@(getppid()),@"executable_path":NSBundle.mainBundle.executablePath?:@"",@"bundle_id":NSBundle.mainBundle.bundleIdentifier?:@"",@"focused_window_supported":@YES,@"request_file_supported":@YES,@"frontmost_pid":@(NSWorkspace.sharedWorkspace.frontmostApplication.processIdentifier)}); return 0; }
    if([action isEqual:@"screen"]) {
        if(!CGPreflightScreenCaptureAccess()) fail(@"Habilite Gravação de Tela para JarvisMacControl em Ajustes do Sistema > Privacidade e Segurança. Depois reinicie o Jarvis.");
        NSString *path=[NSTemporaryDirectory() stringByAppendingPathComponent:[NSUUID.UUID.UUIDString stringByAppendingString:@".png"]];
        NSTask *capture=[NSTask new]; capture.launchPath=@"/usr/sbin/screencapture"; capture.arguments=@[@"-x",@"-D",@"1",path]; capture.standardError=[NSPipe pipe];
        @try { [capture launch]; [capture waitUntilExit]; } @catch(NSException *e) { fail(@"Não foi possível capturar a tela."); }
        if(capture.terminationStatus!=0) { [NSFileManager.defaultManager removeItemAtPath:path error:nil]; fail(@"A captura da tela falhou. Verifique Gravação de Tela."); }
        CGRect screen=CGDisplayBounds(CGMainDisplayID()); CGFloat width=MIN(1280,screen.size.width), height=round(width*screen.size.height/screen.size.width);
        NSData *jpeg=scaledJPEG(path,(size_t)width,(size_t)height);
        [NSFileManager.defaultManager removeItemAtPath:path error:nil];
        if(!jpeg) fail(@"A conversão da captura de tela falhou.");
        emit(@{@"ok":@YES,@"image":[jpeg base64EncodedStringWithOptions:0],@"image_width":@(width),@"image_height":@(height),@"screen_bounds":bounds(screen)}); return 0;
    }
    if(!AXIsProcessTrusted()) fail(@"Habilite Acessibilidade para JarvisMacControl em Ajustes do Sistema > Privacidade e Segurança > Acessibilidade.");
    if(![action isEqual:@"observe"] && !CGPreflightPostEventAccess()) fail(@"Habilite Acessibilidade para JarvisMacControl: a permissão de sintetizar eventos não está disponível.");
    if([action isEqual:@"launch_chrome"]) {
        BOOL clicked=NO;
        for(NSRunningApplication *dock in NSWorkspace.sharedWorkspace.runningApplications) if([dock.bundleIdentifier isEqual:@"com.apple.dock"]) { AXUIElementRef e=AXUIElementCreateApplication(dock.processIdentifier); clicked=clickChrome(e,0); CFRelease(e); }
        if(!clicked) { keyEvent(49,kCGEventFlagMaskCommand); typeEvent(@"Google Chrome"); keyEvent(36,0); }
        if(!CGPreflightPostEventAccess()) fail(@"Habilite Acessibilidade para JarvisMacControl: a permissão de sintetizar eventos não está disponível.");
        emit(@{@"ok":@YES,@"action":action,@"method":clicked?@"dock_mouse":@"spotlight_keyboard",@"event_dispatch":@"posted_not_confirmed"}); return 0;
    }
    pid_t pid=[r[@"pid"] intValue]; NSRunningApplication *app=[NSRunningApplication runningApplicationWithProcessIdentifier:pid];
    if(!app || ![bundles containsObject:app.bundleIdentifier]) fail(@"Aplicativo autorizado indisponível");
    [app activateWithOptions:0]; [NSThread sleepForTimeInterval:0.15];
    AXUIElementRef axapp=AXUIElementCreateApplication(pid);
    NSInteger index=[r[@"window"] integerValue];
    id selected=nil;
    if(index==-1) selected=attr(axapp,@"AXFocusedWindow");
    else { NSArray *windows=attr(axapp,@"AXWindows"); if([windows isKindOfClass:NSArray.class] && index>=0 && index<windows.count) selected=windows[index]; }
    CFRelease(axapp);
    if(!selected || CFGetTypeID((__bridge CFTypeRef)selected)!=AXUIElementGetTypeID()) fail(@"A janela autorizada não está acessível");
    AXUIElementRef window=(__bridge AXUIElementRef)selected;
    NSString *expected=r[@"expected_title"];
    if(expected && ![expected isEqual:attr(window,@"AXTitle")?:@""]) fail(@"A janela mudou desde a observação");
    NSDictionary *expectedBounds=r[@"expected_bounds"]; CGRect currentBounds=frame(window);
    if(expectedBounds) {
        if(![expectedBounds isKindOfClass:NSDictionary.class]) fail(@"Limites de janela inválidos");
        for(NSString *key in @[@"x",@"y",@"width",@"height"]) if(![expectedBounds[key] isKindOfClass:NSNumber.class] || !isfinite([expectedBounds[key] doubleValue])) fail(@"Limites de janela inválidos");
        if(fabs([expectedBounds[@"x"] doubleValue]-currentBounds.origin.x)>1 || fabs([expectedBounds[@"y"] doubleValue]-currentBounds.origin.y)>1 || fabs([expectedBounds[@"width"] doubleValue]-currentBounds.size.width)>1 || fabs([expectedBounds[@"height"] doubleValue]-currentBounds.size.height)>1) fail(@"A posição da janela mudou desde a observação");
    }
    [app activateWithOptions:0]; AXUIElementPerformAction(window,kAXRaiseAction); [NSThread sleepForTimeInterval:0.15];
    if(NSWorkspace.sharedWorkspace.frontmostApplication.processIdentifier!=pid) fail(@"O aplicativo autorizado não está em primeiro plano");
    if([action isEqual:@"observe"]) { NSMutableArray *nodes=[NSMutableArray array]; int count=0; walk(window,0,nodes,&count); emit(@{@"ok":@YES,@"title":attr(window,@"AXTitle")?:@"",@"nodes":nodes,@"window_bounds":bounds(frame(window)),@"pid":@(pid),@"frontmost_pid":@(NSWorkspace.sharedWorkspace.frontmostApplication.processIdentifier),@"window_selection":index==-1?@"focused":@"index"}); return 0; }
    if([action isEqual:@"click"] || [action isEqual:@"move"]) {
        if(![r[@"x"] isKindOfClass:NSNumber.class] || ![r[@"y"] isKindOfClass:NSNumber.class]) fail(@"Coordenadas inválidas");
        CGPoint p=CGPointMake([r[@"x"] doubleValue],[r[@"y"] doubleValue]); if(!CGRectContainsPoint(frame(window),p)) fail(@"Coordenadas fora da janela autorizada");
        if([action isEqual:@"click"]) clickPoint(p); else movePoint(p);
    } else if([action isEqual:@"type"]) {
        NSString *text=r[@"text"]; if(![text isKindOfClass:NSString.class] || text.length>4000) fail(@"Texto inválido");
        typeEvent(text);
    } else if([action isEqual:@"key"]) {
        NSDictionary *keys=@{@"enter":@36,@"tab":@48,@"escape":@53,@"backspace":@51,@"down":@125,@"up":@126,@"left":@123,@"right":@124,@"space":@49,@"page_down":@121,@"page_up":@116,@"cmd+l":@37,@"cmd+a":@0,@"cmd+c":@8,@"cmd+v":@9,@"cmd+f":@3,@"cmd+s":@1,@"cmd+t":@17};
        NSString *key=r[@"key"]; NSNumber *code=keys[key]; if(!code) fail(@"Tecla não permitida");
        keyEvent(code.unsignedShortValue,[key hasPrefix:@"cmd+"]?kCGEventFlagMaskCommand:0);
    } else if([action isEqual:@"scroll"]) {
        int lines=MAX(-12,MIN(12,[r[@"lines"] intValue])); CGEventRef event=CGEventCreateScrollWheelEvent(NULL,kCGScrollEventUnitLine,1,lines); CGEventPost(kCGHIDEventTap,event); CFRelease(event);
    } else fail(@"Ação desconhecida");
    [NSThread sleepForTimeInterval:0.2];
    if(!CGPreflightPostEventAccess()) fail(@"Habilite Acessibilidade para JarvisMacControl: a permissão de sintetizar eventos não está disponível.");
    emit(@{@"ok":@YES,@"action":action,@"bundle":app.bundleIdentifier,@"pid":@(pid),@"frontmost_pid":@(NSWorkspace.sharedWorkspace.frontmostApplication.processIdentifier),@"title":attr(window,@"AXTitle")?:@"",@"window_bounds":bounds(frame(window)),@"cursor":cursorPosition(),@"event_dispatch":@"posted_not_confirmed"});
} return 0; }
