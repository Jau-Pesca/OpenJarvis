#define main native_main
#include "../../../scripts/local/mac-control/control.m"
#undef main
#import <assert.h>

int main(void) { @autoreleasepool {
    NSString *directory=[NSTemporaryDirectory() stringByAppendingPathComponent:NSUUID.UUID.UUIDString];
    assert([NSFileManager.defaultManager createDirectoryAtPath:directory withIntermediateDirectories:NO attributes:@{NSFilePosixPermissions:@0700} error:nil]);
    NSString *path=[directory stringByAppendingPathComponent:@"fixture.png"];
    NSBitmapImageRep *fixture=[[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:64 pixelsHigh:64 bitsPerSample:8 samplesPerPixel:3 hasAlpha:NO isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
    for(int y=0;y<64;y++) for(int x=0;x<64;x++) { NSUInteger pixel[3]={220,40,20}; [fixture setPixel:pixel atX:x y:y]; }
    assert([[fixture representationUsingType:NSBitmapImageFileTypePNG properties:@{}] writeToFile:path atomically:YES]);
    // Reproduce the former AppKit drawing path without initializing NSApplication.
    NSImage *source=[[NSImage alloc] initWithContentsOfFile:path];
    NSBitmapImageRep *previous=[[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:32 pixelsHigh:32 bitsPerSample:8 samplesPerPixel:3 hasAlpha:NO isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
    [NSGraphicsContext saveGraphicsState];
    NSGraphicsContext.currentContext=[NSGraphicsContext graphicsContextWithBitmapImageRep:previous];
    [source drawInRect:NSMakeRect(0,0,32,32)];
    [NSGraphicsContext restoreGraphicsState];
    NSUInteger oldPixel[4]={0}; [previous getPixel:oldPixel atX:16 y:16];
    printf("former drawInRect center RGB=%lu,%lu,%lu\n",oldPixel[0],oldPixel[1],oldPixel[2]);
    NSData *jpeg=scaledJPEG(path,32,32);
    assert(jpeg);
    NSBitmapImageRep *actual=[NSBitmapImageRep imageRepWithData:jpeg];
    NSUInteger pixel[4]={0}; [actual getPixel:pixel atX:16 y:16];
    assert(actual.pixelsWide==32 && actual.pixelsHigh==32);
    assert(labs((long)pixel[0]-220)<=4 && labs((long)pixel[1]-40)<=4 && labs((long)pixel[2]-20)<=4);
    assert(scaledJPEG([directory stringByAppendingPathComponent:@"absent.png"],32,32)==nil);
    printf("CoreGraphics resize JPEG center RGB=%lu,%lu,%lu: PASS\n",pixel[0],pixel[1],pixel[2]);
    [NSFileManager.defaultManager removeItemAtPath:directory error:nil];
} }
