/*
=========================================================
Assignment 3
Raw Socket Packet Analysis
=========================================================
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/socket.h>

#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip_icmp.h>

#define BUFFER_SIZE 65536

/* Function Prototype */

void process_packet(unsigned char *buffer,
                    int size,
                    int packet_no,
                    int protocol,
                    FILE *fp);
int main()
{
    int sockfd;
    int data_size;

    int packet_no = 1;
    int total_packets;

    char roll_no[30];
    int last_digit;

    int protocol;
    char protocol_name[20];

    unsigned char *buffer;

    struct sockaddr saddr;
    socklen_t saddr_len = sizeof(saddr);

    FILE *fp;

    buffer = (unsigned char *)malloc(BUFFER_SIZE);

    if(buffer == NULL)
    {
        printf("Memory Allocation Failed\n");
        return 1;
    }
        printf("========================================\n");
    printf("Raw Socket Packet Capture Program\n");
    printf("========================================\n\n");

    printf("Enter Roll Number : ");
    scanf("%s", roll_no);

    last_digit = roll_no[strlen(roll_no)-1] - '0';

    if(last_digit >=0 && last_digit <=3)
    {
        protocol = IPPROTO_ICMP;
        strcpy(protocol_name,"ICMP");
    }
    else if(last_digit >=4 && last_digit <=6)
    {
        protocol = IPPROTO_UDP;
        strcpy(protocol_name,"UDP");
    }
    else
    {
        protocol = IPPROTO_TCP;
        strcpy(protocol_name,"TCP");
    }

    printf("\nAssigned Protocol : %s\n",
            protocol_name);
        printf("Number of Packets to Capture : ");
    scanf("%d",&total_packets);

    if(total_packets < 20)
    {
        total_packets = 20;
    }
        sockfd = socket(AF_INET,
                    SOCK_RAW,
                    protocol);

    if(sockfd < 0)
    {
        perror("Socket Creation Failed");

        free(buffer);

        return 1;
    }

    fp = fopen("program_output.txt","w");

    if(fp == NULL)
    {
        printf("Cannot Create Output File\n");

        close(sockfd);

        free(buffer);

        return 1;
    }
        printf("\n========================================\n");
    printf("Instructions\n");
    printf("========================================\n");

    if(protocol == IPPROTO_TCP)
    {
        printf("Open another terminal.\n");
        printf("Generate TCP traffic.\n");
        printf("Example : curl https://www.google.com\n");
    }

    else if(protocol == IPPROTO_UDP)
    {
        printf("Open another terminal.\n");
        printf("Example :\n");
        printf("echo Hello | nc -u 127.0.0.1 5000\n");
    }

    else
    {
        printf("Open another terminal.\n");
        printf("Run\n");
        printf("ping -c 5 8.8.8.8\n");
    }

    printf("\nPress ENTER to Start...");

    getchar();
    getchar();
        while(packet_no <= total_packets)
    {

        data_size = recvfrom(sockfd,
                             buffer,
                             BUFFER_SIZE,
                             0,
                             &saddr,
                             &saddr_len);

        if(data_size < 0)
        {
            perror("Receive Failed");
            break;
        }

        process_packet(buffer,
                       data_size,
                       packet_no,
                       protocol,
                       fp);

        packet_no++;

    }
        fclose(fp);

    close(sockfd);

    free(buffer);

    printf("\n========================================\n");
    printf("Capture Completed Successfully\n");
    printf("Saved File : program_output.txt\n");
    printf("========================================\n");

    return 0;
}
void process_packet(unsigned char *buffer,
                    int size,
                    int packet_no,
                    int protocol,
                    FILE *fp)
{
    struct iphdr *ip_header;

    struct sockaddr_in source;
    struct sockaddr_in destination;

    memset(&source,0,sizeof(source));
    memset(&destination,0,sizeof(destination));

    ip_header = (struct iphdr *)buffer;

    /* Ignore packets of other protocols */

    if(ip_header->protocol != protocol)
    {
        return;
    }

    source.sin_addr.s_addr = ip_header->saddr;
    destination.sin_addr.s_addr = ip_header->daddr;

    printf("\n========================================\n");
    printf("PACKET_NO = %d\n",packet_no);
    printf("========================================\n");

    fprintf(fp,"\n========================================\n");
    fprintf(fp,"PACKET_NO = %d\n",packet_no);
    fprintf(fp,"========================================\n");

    printf("SRC_IP          = %s\n",
           inet_ntoa(source.sin_addr));

    fprintf(fp,"SRC_IP          = %s\n",
            inet_ntoa(source.sin_addr));

    printf("DST_IP          = %s\n",
           inet_ntoa(destination.sin_addr));

    fprintf(fp,"DST_IP          = %s\n",
            inet_ntoa(destination.sin_addr));

    printf("PROTOCOL_NO     = %d\n",
            ip_header->protocol);

    fprintf(fp,"PROTOCOL_NO     = %d\n",
            ip_header->protocol);

    printf("TTL             = %d\n",
            ip_header->ttl);

    fprintf(fp,"TTL             = %d\n",
            ip_header->ttl);

    printf("PACKET_SIZE     = %d Bytes\n",
            size);

    fprintf(fp,"PACKET_SIZE     = %d Bytes\n",
            size);

    printf("IP_VERSION      = %d\n",
            ip_header->version);

    fprintf(fp,"IP_VERSION      = %d\n",
            ip_header->version);

    printf("HEADER_LENGTH   = %d Bytes\n",
            ip_header->ihl*4);

    fprintf(fp,"HEADER_LENGTH   = %d Bytes\n",
            ip_header->ihl*4);

    printf("IDENTIFICATION  = %d\n",
            ntohs(ip_header->id));

    fprintf(fp,"IDENTIFICATION  = %d\n",
            ntohs(ip_header->id));
        /*==========================================
      TCP HEADER
    ==========================================*/

    if(protocol == IPPROTO_TCP)
    {
        struct tcphdr *tcp_header;

        tcp_header = (struct tcphdr *)
        (buffer + (ip_header->ihl * 4));

        printf("SRC_PORT        = %u\n",
               ntohs(tcp_header->source));

        fprintf(fp,"SRC_PORT        = %u\n",
                ntohs(tcp_header->source));

        printf("DST_PORT        = %u\n",
               ntohs(tcp_header->dest));

        fprintf(fp,"DST_PORT        = %u\n",
                ntohs(tcp_header->dest));

        printf("TCP_FLAGS       = ");

        fprintf(fp,"TCP_FLAGS       = ");

        if(tcp_header->syn)
        {
            printf("SYN ");
            fprintf(fp,"SYN ");
        }

        if(tcp_header->ack)
        {
            printf("ACK ");
            fprintf(fp,"ACK ");
        }

        if(tcp_header->fin)
        {
            printf("FIN ");
            fprintf(fp,"FIN ");
        }

        if(tcp_header->rst)
        {
            printf("RST ");
            fprintf(fp,"RST ");
        }

        if(tcp_header->psh)
        {
            printf("PSH ");
            fprintf(fp,"PSH ");
        }

        if(tcp_header->urg)
        {
            printf("URG ");
            fprintf(fp,"URG ");
        }

        printf("\n");
        fprintf(fp,"\n");
    }

    /*==========================================
      UDP HEADER
    ==========================================*/

    else if(protocol == IPPROTO_UDP)
    {
        struct udphdr *udp_header;

        udp_header = (struct udphdr *)
        (buffer + (ip_header->ihl * 4));

        printf("SRC_PORT        = %u\n",
               ntohs(udp_header->source));

        fprintf(fp,"SRC_PORT        = %u\n",
                ntohs(udp_header->source));

        printf("DST_PORT        = %u\n",
               ntohs(udp_header->dest));

        fprintf(fp,"DST_PORT        = %u\n",
                ntohs(udp_header->dest));

        printf("UDP_LENGTH      = %u\n",
               ntohs(udp_header->len));

        fprintf(fp,"UDP_LENGTH      = %u\n",
                ntohs(udp_header->len));
    }

    /*==========================================
      ICMP HEADER
    ==========================================*/

    else if(protocol == IPPROTO_ICMP)
    {
        struct icmphdr *icmp_header;

        icmp_header = (struct icmphdr *)
        (buffer + (ip_header->ihl * 4));

        printf("ICMP_TYPE       = %u\n",
               icmp_header->type);

        fprintf(fp,"ICMP_TYPE       = %u\n",
                icmp_header->type);

        printf("ICMP_CODE       = %u\n",
               icmp_header->code);

        fprintf(fp,"ICMP_CODE       = %u\n",
                icmp_header->code);
    }

    printf("\n");

    fprintf(fp,"\n");
}
