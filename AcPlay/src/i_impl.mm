// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS
#import "ViewController.h"
#include <includes.h>


// A custom UIView to receive input events


// Register the custom UIView into ViewController
@interface ViewController
@property(nonatomic, strong) UIView *ArInput;
@end

@implementation ViewController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.ArInput = [[UIView alloc] initWithFrame: [[UIScreen mainScreen] bounds] ];
    [self.view addSubview:self.ArInput];
}
@end

#endif