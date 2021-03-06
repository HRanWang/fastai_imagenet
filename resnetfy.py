import torch.nn as nn
import torch
import numpy as np


def SpatialAttn_whr(x):
    """Spatial Attention"""
    x_shape = x.size()
    a = x.sum(1, keepdim=True)
    a = a.view(x_shape[0], -1)
    a = a / a.sum(1, keepdim=True)
    a = a.view(x_shape[0], 1, x_shape[2], x_shape[3])
    return a



def ChannelAttn_whr(x):
    """Channel Attention"""
    x_shape = x.size()
    x = x.view(x_shape[0], x_shape[1], -1)  # [bs, c, h*w]
    a = x.sum(-1, keepdim=False)  # [bs, c]
    a /= a.sum(1, keepdim=True)  # [bs, c]
    a = a.unsqueeze(-1).unsqueeze(-1)
    return a


def conv_1_3x3():
    return nn.Sequential(nn.Conv2d(3, 16*4, kernel_size=3, stride=1, padding=1, bias=False),  # 'SAME'
                         nn.BatchNorm2d(16*4),
                         nn.ReLU(inplace=True))
                         # TODO: nn.MaxPool2d(kernel_size=3, stride=2, padding=0))  # 'valid'


class identity_block3(nn.Module):
    def __init__(self, inplanes, planes, kernel_size):
        super(identity_block3, self).__init__()
        plane1, plane2, plane3 = planes
        self.conv1 = nn.Conv2d(inplanes, plane1, kernel_size=1, stride=1, padding=0, bias=False)
        self.bn1 = nn.BatchNorm2d(plane1)
        self.conv2 = nn.Conv2d(plane1, plane2, kernel_size=kernel_size, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(plane2)
        self.conv3 = nn.Conv2d(plane2, plane3, kernel_size=1, stride=1, padding=0, bias=False)
        self.bn3 = nn.BatchNorm2d(plane3)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, input_tensor):
        out = self.conv1(input_tensor)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        out += input_tensor
        out = self.relu(out)
        return out


class bottleneck(nn.Module):
    def __init__(self, inplanes, planes, kernel_size, strides=(2, 2)):
        super(bottleneck, self).__init__()
        plane1, plane2, plane3 = planes
        self.conv1 = nn.Conv2d(inplanes, plane1, kernel_size=1, stride=strides, padding=0, bias=False)
        self.bn1 = nn.BatchNorm2d(plane1)
        self.conv2 = nn.Conv2d(plane1, plane2, kernel_size=kernel_size, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(plane2)
        self.conv3 = nn.Conv2d(plane2, plane3, kernel_size=1, stride=1, padding=0, bias=False)
        self.bn3 = nn.BatchNorm2d(plane3)
        self.conv4 = nn.Conv2d(inplanes, plane3, kernel_size=1, stride=strides, padding=0, bias=False)
        self.bn4 = nn.BatchNorm2d(plane3)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, input_tensor):
        out = self.conv1(input_tensor)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        shortcut = self.conv4(input_tensor)
        shortcut = self.bn4(shortcut)

        out += shortcut
        out = self.relu(out)
        return out

class bottleneck_dconv():
    pass
class identity_block3_dconv():
    pass

class Resnet50(nn.Module):
    def __init__(self, dropout_rate, num_classes, include_top, layer, type='none'):
        print('resnet50 is used')
        super(Resnet50, self).__init__()
        self.dropout_rate = dropout_rate
        self.num_classes = num_classes
        self.include_top = include_top

        # Define the building blocks
        self.conv_3x3 = conv_1_3x3()  # TODO: check if you are using dconv3x3

        if layer > 10:
            self.bottleneck_1 = bottleneck(16*4, [16*4, 16*4, 64*4], kernel_size=3, strides=(1, 1))
        else:
            self.bottleneck_1 = bottleneck_dconv(16, [16, 16, 64], kernel_size=3, strides=(1, 1), type=type)
        if layer > 11:
            self.identity_block_1_1 = identity_block3(64*4, [16*4, 16*4, 64*4], kernel_size=3)
        else:
            self.identity_block_1_1 = identity_block3_dconv(64, [16, 16, 64], kernel_size=3, type=type)
        if layer > 12:
            self.identity_block_1_2 = identity_block3(64*4, [16*4, 16*4, 64*4], kernel_size=3)
        else:
            self.identity_block_1_2 = identity_block3_dconv(64, [16, 16, 64], kernel_size=3, type=type)

        if layer > 20:
            self.bottleneck_2 = bottleneck(64*4, [32*4, 32*4, 128*4], kernel_size=3, strides=(2, 2))
        else:
            self.bottleneck_2 = bottleneck_dconv(64, [32, 32, 128], kernel_size=3, strides=(2, 2), type=type)
        if layer > 21:
            self.identity_block_2_1 = identity_block3(128*4, [32*4, 32*4, 128*4], kernel_size=3)
        else:
            self.identity_block_2_1 = identity_block3_dconv(128, [32, 32, 128], kernel_size=3, type=type)
        if layer > 22:
            self.identity_block_2_2 = identity_block3(128*4, [32*4, 32*4, 128*4], kernel_size=3)
        else:
            self.identity_block_2_2 = identity_block3_dconv(128, [32, 32, 128], kernel_size=3, type=type)
        if layer > 23:
            self.identity_block_2_3 = identity_block3(128*4, [32*4, 32*4, 128*4], kernel_size=3)
        else:
            self.identity_block_2_3 = identity_block3_dconv(128, [32, 32, 128], kernel_size=3, type=type)

        if layer > 30:
            self.bottleneck_3 = bottleneck(128*4, [64*4, 64*4, 256*4], kernel_size=3, strides=(2, 2))
        else:
            self.bottleneck_3 = bottleneck_dconv(128, [64, 64, 256], kernel_size=3, strides=(2, 2), type=type)
        if layer > 31:
            self.identity_block_3_1 = identity_block3(256*4, [64*4, 64*4, 256*4], kernel_size=3)
        else:
            self.identity_block_3_1 = identity_block3_dconv(256, [64, 64, 256], kernel_size=3, type=type)
        if layer > 32:
            self.identity_block_3_2 = identity_block3(256*4, [64*4, 64*4, 256*4], kernel_size=3)
        else:
            self.identity_block_3_2 = identity_block3_dconv(256, [64, 64, 256], kernel_size=3, type=type)
        if layer > 33:
            self.identity_block_3_3 = identity_block3(256*4, [64*4, 64*4, 256*4], kernel_size=3)
        else:
            self.identity_block_3_3 = identity_block3_dconv(256, [64, 64, 256], kernel_size=3, type=type)
        if layer > 34:
            self.identity_block_3_4 = identity_block3(256*4, [64*4, 64*4, 256*4], kernel_size=3)
        else:
            self.identity_block_3_4 = identity_block3_dconv(256, [64, 64, 256], kernel_size=3, type=type)
        if layer > 35:
            self.identity_block_3_5 = identity_block3(256*4, [64*4, 64*4, 256*4], kernel_size=3)
        else:
            self.identity_block_3_5 = identity_block3_dconv(256, [64, 64, 256], kernel_size=3, type=type)

        if layer > 40:
            self.bottleneck_4 = bottleneck(256*4, [128*4, 128*4, 512*4], kernel_size=3, strides=(2, 2))
        else:
            self.bottleneck_4 = bottleneck_dconv(256, [128, 128, 512], kernel_size=3, strides=(2, 2), type=type)
        if layer > 41:
            self.identity_block_4_1 = identity_block3(512*4, [128*4, 128*4, 512*4], kernel_size=3)
        else:
            self.identity_block_4_1 = identity_block3_dconv(512, [128, 128, 512], kernel_size=3, type=type)
        if layer > 42:
            self.identity_block_4_2 = identity_block3(512*4, [128*4, 128*4, 512*4], kernel_size=3)
        else:
            self.identity_block_4_2 = identity_block3_dconv(512, [128, 128, 512], kernel_size=3, type=type)

        self.avgpool = nn.AvgPool2d(4)  # TODO: check the final size
        self.fc = nn.Linear(512*4, num_classes)
        # self.sa = SpatialAttn_whr()
        # Initialize the weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                # raise Exception('You are using a model without BN!!!')
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, input_x):
        # print(input_x.size())
        x = self.conv_3x3(input_x)
        # np.save('/nethome/yuefan/fanyue/dconv/fm3x3.npy', x.detach().cpu().numpy())
        # print(x.size())
        x = self.bottleneck_1(x)
        x = self.identity_block_1_1(x)
        x = self.identity_block_1_2(x)

        # print(x.size())
        x = self.bottleneck_2(x)
        x = self.identity_block_2_1(x)
        x = self.identity_block_2_2(x)
        x = self.identity_block_2_3(x)
        x = x * SpatialAttn_whr(x)
        # print(x.size())
        x = self.bottleneck_3(x)
        x = self.identity_block_3_1(x)
        x = self.identity_block_3_2(x)
        x = self.identity_block_3_3(x)
        x = self.identity_block_3_4(x)
        x = self.identity_block_3_5(x)
        # print(x.size())
        x = self.bottleneck_4(x)
        x = self.identity_block_4_1(x)
        x = self.identity_block_4_2(x)
        # print("feature shape:", x.size())

        if self.include_top:
            x = self.avgpool(x)
            x = x.view(x.size(0), -1)
            # TODO: why there is no dropout
            x = self.fc(x)
        return x
