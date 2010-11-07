#include<stdio.h>
#include "mything.h"


int get_thing_one()
{
    return THING_ONE;
}

int get_thing_two()
{
    return THING_TWO;
}

int main()
{
    int thing1;
    int thing2;
    thing1 = get_thing_one();
    thing2 = get_thing_two();
    printf("\nThing One: %d\nThing Two: %d\n", thing1, thing2);
    return 0;
}
