// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS
#include <includes.h>


// A custom UIView to receive input events
#import <UIKit/UIKit.h>
@interface ArInput : UIView @end
@implementation ArInput

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    UITouch *touch = [touches anyObject];
    CGPoint location = [touch locationInView:self];
    NSLog(@"Touch began at location: %@", NSStringFromCGPoint(location));

    // ···
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    UITouch *touch = [touches anyObject];
    CGPoint location = [touch locationInView:self];
    NSLog(@"Touch moved to location: %@", NSStringFromCGPoint(location));

    // ···
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    NSLog(@"Touch ended");

    // ···
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    NSLog(@"Touch cancelled");

    // ···
}

@end


// Register the custom UIView into ViewController
#import "ViewController.h"
@interface ViewController () @end
@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    ArInput *AIview = [ [ArInput alloc] initWithFrame: self.view.bounds ];
    AIview.userInteractionEnabled = YES;
    [self.view addSubview:AIview];
}

@end


#endif