#include <stdio.h>
#include <sys/ioctl.h>

#include <linux/dvb/frontend.h>

int main() {
    printf("ioctl values calculated in C:\n");
    printf("FE_SET_TONE: 0x%x\n", FE_SET_TONE);
    printf("FE_SET_VOLTAGE: 0x%x\n", FE_SET_VOLTAGE);
    printf("FE_ENABLE_HIGH_LNB_VOLTAGE: 0x%x\n", FE_ENABLE_HIGH_LNB_VOLTAGE);
    printf("FE_DISEQC_SEND_MASTER_CMD: 0x%lx\n", FE_DISEQC_SEND_MASTER_CMD);
    printf("FE_DISEQC_RECV_SLAVE_REPLY: 0x%lx\n", FE_DISEQC_RECV_SLAVE_REPLY);
}
