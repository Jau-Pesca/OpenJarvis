#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#import <assert.h>

static int recorded=0;
static CGEventFlags recordedFlags[100];
static int unicodeUnits[100];
static CGKeyCode keyCodes[100];
static void capture(CGEventTapLocation location, CGEventRef event) {
    assert(location==kCGHIDEventTap && recorded<100);
    recordedFlags[recorded]=CGEventGetFlags(event);
    keyCodes[recorded]=(CGKeyCode)CGEventGetIntegerValueField(event,kCGKeyboardEventKeycode);
    UniChar text[16]; UniCharCount count=0;
    CGEventKeyboardGetUnicodeString(event,16,&count,text);
    unicodeUnits[recorded]=(int)count;
    recorded++;
}
// Every publish call is intercepted. This fixture never posts physical events.
#define CGEventPost capture
#define main native_main
#include "../../../scripts/local/mac-control/control.m"
#undef main
#undef CGEventPost

int main(void) { @autoreleasepool {
    keyEvent(0,kCGEventFlagMaskCommand);
    assert(recorded==4);
    assert(keyCodes[0]==55 && keyCodes[1]==0 && keyCodes[2]==0 && keyCodes[3]==55);
    assert(recordedFlags[0]==kCGEventFlagMaskCommand && recordedFlags[1]==kCGEventFlagMaskCommand && recordedFlags[2]==kCGEventFlagMaskCommand && recordedFlags[3]==0);
    typeEvent(@"a😀b");
    assert(recorded==10);
    for(int i=4;i<10;i++) assert(recordedFlags[i]==0);
    assert(unicodeUnits[4]==1 && unicodeUnits[5]==1 && unicodeUnits[6]==2 && unicodeUnits[7]==2 && unicodeUnits[8]==1 && unicodeUnits[9]==1);
    keyEvent(36,0);
    assert(recorded==12 && recordedFlags[10]==0 && recordedFlags[11]==0);
    assert(keyCodes[10]==36 && keyCodes[11]==36);
    printf("Command release, Unicode codepoints and Enter flags: PASS (12 intercepted events, none posted)\n");
} }
